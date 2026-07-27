"""Read/write helpers for the DataPoint ledger (see app/models/datapoint.py).

This is the only sanctioned way engines should write facts - it enforces
the append-only/never-overwrite rule (Regel C.19) and the "UNKNOWN is
never silently upgraded" rule (Regel C.3) at a single choke point.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import DataStatus
from app.models.datapoint import DataPoint, ValueType

_VALUE_COLUMNS = {
    ValueType.MONEY_CENTS: "value_int",
    ValueType.DECIMAL: "value_numeric",
    ValueType.INTEGER: "value_int",
    ValueType.TEXT: "value_text",
    ValueType.BOOLEAN: "value_bool",
    ValueType.DATE: "value_date",
    ValueType.JSON: "value_json",
}


def get_current_fact(session: Session, entity_type: str, entity_id: uuid.UUID, field_name: str) -> DataPoint | None:
    stmt = select(DataPoint).where(
        DataPoint.entity_type == entity_type,
        DataPoint.entity_id == entity_id,
        DataPoint.field_name == field_name,
        DataPoint.is_current.is_(True),
    )
    return session.scalars(stmt).one_or_none()


def get_fact_history(session: Session, entity_type: str, entity_id: uuid.UUID, field_name: str) -> list[DataPoint]:
    stmt = (
        select(DataPoint)
        .where(
            DataPoint.entity_type == entity_type,
            DataPoint.entity_id == entity_id,
            DataPoint.field_name == field_name,
        )
        .order_by(DataPoint.recorded_at.asc())
    )
    return list(session.scalars(stmt).all())


def record_fact(
    session: Session,
    *,
    entity_type: str,
    entity_id: uuid.UUID,
    field_name: str,
    status: DataStatus,
    value_type: ValueType,
    value: Any,
    recorded_by: str,
    unit: str | None = None,
    source_record_id: uuid.UUID | None = None,
    confidence_score: Decimal | None = None,
    confidence_breakdown: dict | None = None,
    notes: str | None = None,
    valid_from: date | None = None,
    valid_until: date | None = None,
    supersedes_reason: str | None = None,
) -> DataPoint:
    """Insert a new current fact, superseding (never deleting) any prior one.

    Regel C.3: callers must not pass status=UNKNOWN just because a value
    happens to be falsy/zero, and must not silently upgrade an existing
    UNKNOWN fact into something else without genuinely new evidence
    (source_record_id or notes explaining the change).
    """
    if status in (DataStatus.VERIFIED, DataStatus.DOCUMENTED, DataStatus.OBSERVED) and source_record_id is None:
        raise ValueError(f"status={status} requires a source_record_id (Regel C.1)")
    if status == DataStatus.UNKNOWN and value is not None:
        raise ValueError("status=UNKNOWN must not carry a concrete value (Regel C.3/C.48)")

    previous = get_current_fact(session, entity_type, entity_id, field_name)

    new_point = DataPoint(
        entity_type=entity_type,
        entity_id=entity_id,
        field_name=field_name,
        status=status,
        value_type=value_type,
        unit=unit,
        source_record_id=source_record_id,
        confidence_score=confidence_score,
        confidence_breakdown=confidence_breakdown,
        notes=notes,
        valid_from=valid_from,
        valid_until=valid_until,
        recorded_by=recorded_by,
        is_current=True,
    )
    setattr(new_point, _VALUE_COLUMNS[value_type], value)

    session.add(new_point)
    session.flush()  # need new_point.id before linking

    if previous is not None:
        previous.is_current = False
        previous.superseded_by_id = new_point.id
        previous.supersedes_reason = supersedes_reason or "superseded by newer fact"

    return new_point


def read_value(point: DataPoint | None) -> Any:
    """Convenience accessor. Returns None for UNKNOWN/missing - callers
    must handle None as 'unknown', never coerce it to 0/False (Regel C.26
    of the acceptance tests, Teil J.26)."""
    if point is None:
        return None
    if point.status in (DataStatus.UNKNOWN, DataStatus.CONFLICTING, DataStatus.NOT_APPLICABLE):
        return None
    return getattr(point, _VALUE_COLUMNS[point.value_type])
