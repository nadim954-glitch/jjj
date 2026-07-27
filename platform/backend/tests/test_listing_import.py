"""Engine 01 tests: Regel 01.9-01.14 (snapshots/price history), 01.19/13.8
(commission never defaults to 0), 01.29-01.31 (keyword screening),
01.41-01.44 (text-vs-field conflicts)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.enums import DataStatus, ListingKind, PropertyType, TenancyStatus
from app.engines.listing_import import ListingInputRow, import_csv, import_listing, price_history
from app.models.listing import Listing


def test_same_external_id_creates_snapshot_not_duplicate_listing(session, manual_source):
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    row1 = ListingInputRow(
        external_listing_id="EX-1",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        asking_price_eur=Decimal("300000"),
        living_area_listing_sqm=Decimal("80"),
    )
    result1 = import_listing(session, source=manual_source, row=row1, recorded_by="tester", retrieved_at=t0)
    assert result1.is_new_listing is True

    t1 = t0 + timedelta(days=30)
    row2 = ListingInputRow(
        external_listing_id="EX-1",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        asking_price_eur=Decimal("285000"),
        living_area_listing_sqm=Decimal("80"),
    )
    result2 = import_listing(session, source=manual_source, row=row2, recorded_by="tester", retrieved_at=t1)
    session.commit()

    assert result2.is_new_listing is False
    assert result2.listing.id == result1.listing.id

    listing = session.get(Listing, result1.listing.id)
    assert len(listing.snapshots) == 2  # Regel 01.10: history retained, not overwritten (Test J.12)


def test_price_history_absolute_and_percent_change(session, manual_source):
    t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
    row1 = ListingInputRow(
        external_listing_id="EX-2",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        asking_price_eur=Decimal("300000"),
    )
    r1 = import_listing(session, source=manual_source, row=row1, recorded_by="tester", retrieved_at=t0)

    t1 = t0 + timedelta(days=45)
    row2 = ListingInputRow(
        external_listing_id="EX-2",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        asking_price_eur=Decimal("270000"),
    )
    import_listing(session, source=manual_source, row=row2, recorded_by="tester", retrieved_at=t1)
    session.commit()

    history = price_history(r1.listing)
    assert history[0]["absolute_change_cents"] is None
    assert history[1]["absolute_change_cents"] == -3000000
    assert history[1]["percent_change"] == Decimal("-10.00")
    assert history[1]["days_since_previous"] == 45


def test_unclear_commission_stays_unknown_never_zero(session, manual_source):
    row = ListingInputRow(
        external_listing_id="EX-3",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        asking_price_eur=Decimal("250000"),
        commission_eur=None,
        commission_status=DataStatus.UNKNOWN,
    )
    result = import_listing(session, source=manual_source, row=row, recorded_by="tester")
    session.commit()

    assert result.snapshot.commission_cents is None
    assert result.snapshot.commission_status == DataStatus.UNKNOWN
    assert any("courtage" in w.lower() for w in result.warnings)


def test_renovation_and_damage_keyword_screening(session, manual_source):
    row = ListingInputRow(
        external_listing_id="EX-4",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        description_text="Sanierungsbedürftige Wohnung, im Bad war früher ein Wasserschaden.",
    )
    result = import_listing(session, source=manual_source, row=row, recorded_by="tester")
    session.commit()

    assert "sanierungsbedürftig" in result.snapshot.renovation_keyword_hits
    assert "wasserschaden" in result.snapshot.damage_keyword_hits


def test_text_vs_structured_area_conflict_detected(session, manual_source):
    row = ListingInputRow(
        external_listing_id="EX-5",
        listing_kind=ListingKind.PURCHASE,
        property_type=PropertyType.CONDOMINIUM_UNIT,
        living_area_listing_sqm=Decimal("60"),
        description_text="Große Wohnung mit ca. 95 m² Wohnfläche.",
    )
    result = import_listing(session, source=manual_source, row=row, recorded_by="tester")
    session.commit()

    assert len(result.conflicts) == 1
    assert result.conflicts[0]["field"] == "living_area_listing_sqm"


def test_csv_import_creates_one_listing_per_row(session, manual_source):
    csv_text = (
        "external_listing_id,property_type,asking_price_eur,living_area_sqm\n"
        "CSV-1,CONDOMINIUM_UNIT,200000,55\n"
        "CSV-2,CONDOMINIUM_UNIT,310000,72\n"
    )
    results = import_csv(session, source=manual_source, csv_text=csv_text, recorded_by="tester")
    session.commit()
    assert len(results) == 2
    assert {r.listing.external_listing_id for r in results} == {"CSV-1", "CSV-2"}
