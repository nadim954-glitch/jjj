"""Generic, append-only fact ledger.

Every substantive fact in the system (a price, an area, a year built, a
condition rating, ...) is stored as a `DataPoint` row rather than a bare
column, so that Regel C.1 (origin must be stored), C.2 (status vocabulary),
C.17-C.20 (reproducible, versioned, never overwritten) and Engine 03's
provenance requirements apply uniformly instead of being reinvented per
field. Structural/identity columns (an Address's street name, a Listing's
FK to a Property) stay as normal typed columns on their entity tables -
DataPoint is for facts that can be wrong, contested, or superseded.

This is a typed EAV table, not a "loose JSON blob" (Teil D's prohibition):
every value is stored in a properly typed column selected by `value_type`,
and every row is queryable/joinable via entity_type + entity_id + field_name.
"""
from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DataStatus
from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin, utcnow


class ValueType(str, enum.Enum):
    MONEY_CENTS = "MONEY_CENTS"
    DECIMAL = "DECIMAL"
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    JSON = "JSON"


class DataPoint(UUIDPKMixin, Base):
    __tablename__ = "data_points"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    status: Mapped[DataStatus] = mapped_column(Enum(DataStatus, name="data_status"), nullable=False)

    value_type: Mapped[ValueType] = mapped_column(Enum(ValueType, name="value_type"), nullable=False)
    value_numeric: Mapped[object | None] = mapped_column(Numeric(20, 6), nullable=True)
    value_int: Mapped[int | None] = mapped_column(nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_bool: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    value_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    value_json: Mapped[dict | list | None] = mapped_column(JSONVariant, nullable=True)

    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Regel C.1, 03.6-03.8: origin. Only NOT_APPLICABLE/UNKNOWN rows may
    # omit a source record, and even then `notes` must explain why.
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("source_records.id"), nullable=True
    )

    confidence_score: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    confidence_breakdown: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Regel C.42: time-bounded validity for facts that change over time
    # (legal/tax parameters, rent-index values, etc.).
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    recorded_by: Mapped[str] = mapped_column(String(200), nullable=False)

    # Regel C.19-C.20: append-only versioning. The previous "current" row
    # is flipped to is_current=False and linked via superseded_by_id -
    # never deleted or mutated in place.
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    superseded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("data_points.id"), nullable=True
    )
    supersedes_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_record: Mapped["SourceRecord | None"] = relationship()  # noqa: F821
