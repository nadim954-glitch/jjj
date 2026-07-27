"""Engine 05 - Comparable & Market Data.

Regel 05.1-05.5: SOLD_COMPARABLE (actual transaction), ASKING_COMPARABLE
(current/historical offer) and OFFICIAL_AGGREGATE (official aggregate,
e.g. Bodenrichtwert) are strictly separate classes and must never be
silently averaged together unlabeled.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import ComparableClass, EngineStatus
from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin


class ComparableSet(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "comparable_sets"

    subject_unit_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("units.id"), nullable=True)
    subject_property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)

    status: Mapped[EngineStatus] = mapped_column(
        Enum(EngineStatus, name="comparable_set_status"), default=EngineStatus.NOT_STARTED, nullable=False
    )

    search_radius_km_initial: Mapped[object] = mapped_column(Numeric(5, 2), nullable=False)
    search_radius_km_final: Mapped[object] = mapped_column(Numeric(5, 2), nullable=False)
    time_window_months_initial: Mapped[int] = mapped_column(Integer, nullable=False)
    time_window_months_final: Mapped[int] = mapped_column(Integer, nullable=False)

    # Regel 05.13, 05.15: every radius/time expansion step is logged.
    expansion_log: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)

    comparables: Mapped[list["Comparable"]] = relationship(back_populates="comparable_set")


class Comparable(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "comparables"

    comparable_set_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("comparable_sets.id"), nullable=False)
    comparable_class: Mapped[ComparableClass] = mapped_column(
        Enum(ComparableClass, name="comparable_class"), nullable=False
    )
    source_record_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("source_records.id"), nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(300), nullable=True)

    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_date: Mapped[date] = mapped_column(Date, nullable=False)  # transaction/listing/valuation date

    living_area_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    condition_label: Mapped[str | None] = mapped_column(String(60), nullable=True)
    distance_km: Mapped[object | None] = mapped_column(Numeric(6, 3), nullable=True)
    features: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)

    # Regel 05.31-05.34: per-dimension breakdown, not just one opaque number.
    similarity_breakdown: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    similarity_total: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)

    # Regel 05.38-05.41: outliers are flagged, never deleted.
    is_outlier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    outlier_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Regel 05.46, 05.47: currently-marketed comparables' marketing
    # duration and any price reduction are informative, not disqualifying.
    marketing_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    was_price_reduced: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # Regel 05.49: why this comparable was included (or, if excluded, why).
    excluded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    inclusion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    comparable_set: Mapped[ComparableSet] = relationship(back_populates="comparables")


class MarketDataPoint(UUIDPKMixin, TimestampMixin, Base):
    """Official aggregate market figures not tied to one specific
    comparable object, e.g. a Bodenrichtwert zone value (Regel C.8,
    Engine 11) or a rent-index figure (Engine 12)."""

    __tablename__ = "market_data_points"

    source_record_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("source_records.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(150), nullable=False)
    value_numeric: Mapped[object] = mapped_column(Numeric(14, 4), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    geographic_zone: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valuation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
