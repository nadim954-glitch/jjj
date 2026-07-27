"""Regel C.1-C.3, C.17-C.20, Test J.26: DataPoint ledger behaviour."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.core.enums import DataStatus, SourceAccessType, SourceQualityClass
from app.core.provenance_service import get_current_fact, get_fact_history, read_value, record_fact
from app.models.datapoint import ValueType
from app.models.source import Source, SourceRecord


def _make_source_record(session) -> SourceRecord:
    src = Source(
        name=f"Test Source {uuid.uuid4()}",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Berlin",
        content_description="test",
    )
    session.add(src)
    session.flush()
    rec = SourceRecord(
        source_id=src.id,
        retrieved_at=datetime.now(timezone.utc),
        import_method="MANUAL",
    )
    session.add(rec)
    session.flush()
    return rec


def test_verified_fact_requires_source_record(session):
    entity_id = uuid.uuid4()
    with pytest.raises(ValueError):
        record_fact(
            session,
            entity_type="Unit",
            entity_id=entity_id,
            field_name="year_built",
            status=DataStatus.VERIFIED,
            value_type=ValueType.INTEGER,
            value=1965,
            recorded_by="test",
        )


def test_unknown_fact_cannot_carry_a_value(session):
    entity_id = uuid.uuid4()
    with pytest.raises(ValueError):
        record_fact(
            session,
            entity_type="Unit",
            entity_id=entity_id,
            field_name="year_built",
            status=DataStatus.UNKNOWN,
            value_type=ValueType.INTEGER,
            value=1965,
            recorded_by="test",
        )


def test_read_value_of_unknown_is_none_never_zero(session):
    """Test J.26: UNKNOWN must never be treated as 0."""
    entity_id = uuid.uuid4()
    point = record_fact(
        session,
        entity_type="Unit",
        entity_id=entity_id,
        field_name="commission_cents",
        status=DataStatus.UNKNOWN,
        value_type=ValueType.MONEY_CENTS,
        value=None,
        recorded_by="test",
        notes="Courtage nicht im Exposé genannt.",
    )
    assert read_value(point) is None
    assert read_value(point) != 0


def test_new_fact_supersedes_without_deleting_history(session):
    """Regel C.17-C.20: append-only, never overwritten."""
    entity_id = uuid.uuid4()
    rec1 = _make_source_record(session)
    first = record_fact(
        session,
        entity_type="Unit",
        entity_id=entity_id,
        field_name="year_built",
        status=DataStatus.DOCUMENTED,
        value_type=ValueType.INTEGER,
        value=1965,
        recorded_by="importer",
        source_record_id=rec1.id,
    )
    rec2 = _make_source_record(session)
    second = record_fact(
        session,
        entity_type="Unit",
        entity_id=entity_id,
        field_name="year_built",
        status=DataStatus.VERIFIED,
        value_type=ValueType.INTEGER,
        value=1968,
        recorded_by="inspector",
        source_record_id=rec2.id,
        supersedes_reason="Bauakte eingesehen",
    )
    session.flush()

    current = get_current_fact(session, "Unit", entity_id, "year_built")
    assert current.id == second.id
    assert read_value(current) == 1968

    history = get_fact_history(session, "Unit", entity_id, "year_built")
    assert len(history) == 2
    assert history[0].id == first.id
    assert history[0].is_current is False
    assert history[0].superseded_by_id == second.id
    # the old row's value must still be readable, not deleted/blanked
    assert read_value(history[0]) == 1965
