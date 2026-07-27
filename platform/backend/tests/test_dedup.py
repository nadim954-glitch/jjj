"""Engine 02 dedup tests: Regel 02.17-02.23, Test J.11."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.core.enums import ListingKind, PropertyType
from app.engines.dedup import MergeNotJustifiedError, confirm_merge, score_similarity, unmerge
from app.engines.listing_import import ListingInputRow, import_listing
from app.models.audit import AuditLog


def _import(session, source, external_id, address, price, area):
    row = ListingInputRow(
        external_listing_id=external_id,
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        raw_address_text=address,
        asking_price_eur=Decimal(price),
        living_area_listing_sqm=Decimal(area),
    )
    return import_listing(session, source=source, row=row, recorded_by="tester")


def test_single_strong_feature_is_not_enough_to_merge(session, manual_source, sample_property):
    """Regel 02.18: address alone (even if identical) must not
    auto-justify a merge without override."""
    r1 = _import(session, manual_source, "P1", "Musterstraße 1, 10115 Berlin", "300000", "80")
    r2 = _import(session, manual_source, "P2", "Musterstraße 1, 10115 Berlin", "999999", "10")
    session.commit()

    candidate = score_similarity(r1.listing, r2.listing)
    assert candidate.strong_features == ["address"]
    assert candidate.suggested is False

    with pytest.raises(MergeNotJustifiedError):
        confirm_merge(
            session,
            listing_a=r1.listing,
            listing_b=r2.listing,
            candidate=candidate,
            performed_by="tester",
            target_property=sample_property,
        )


def test_matching_address_and_area_suggests_merge_and_keeps_both_listings(session, manual_source, sample_property):
    """Test J.11: two portals, same object -> one Property, two Listings."""
    r1 = _import(session, manual_source, "PORTAL-A-1", "Musterstraße 1, 10115 Berlin", "300000", "80")
    r2 = _import(session, manual_source, "PORTAL-B-1", "Musterstr. 1, 10115 Berlin", "299000", "80.5")
    session.commit()

    candidate = score_similarity(r1.listing, r2.listing)
    assert "address" in candidate.strong_features
    assert "area" in candidate.strong_features
    assert candidate.suggested is True

    target = confirm_merge(
        session,
        listing_a=r1.listing,
        listing_b=r2.listing,
        candidate=candidate,
        performed_by="tester",
        target_property=sample_property,
    )
    session.commit()

    assert r1.listing.property_id == target.id
    assert r2.listing.property_id == target.id
    # Both listings and their own price/snapshot history must survive
    # the merge untouched (Regel 02.23).
    assert len(r1.listing.snapshots) == 1
    assert len(r2.listing.snapshots) == 1
    assert r1.listing.id != r2.listing.id

    audit = session.query(AuditLog).filter_by(action="MERGE_LISTINGS").one()
    assert str(target.id) in str(audit.entity_id)


def test_unmerge_reverses_a_wrong_merge(session, manual_source, sample_property):
    r1 = _import(session, manual_source, "UM-1", "Beispielweg 5, 12345 Berlin", "200000", "50")
    session.commit()
    r1.listing.property_id = sample_property.id
    session.commit()

    unmerge(session, listing=r1.listing, performed_by="tester", reason="Falsch zugeordnet")
    session.commit()

    assert r1.listing.property_id is None
    audit = session.query(AuditLog).filter_by(action="UNMERGE_LISTING").one()
    assert audit.entity_id == r1.listing.id
