"""Engine 06 - Valuation.

Regel 06.17-06.18: AS_IS value is a range (LOW/BASE/HIGH), not a single
number pretending to be precise.
Regel 06.32-06.33: MARKET_VALUE vs. INDICATIVE_VALUE - insufficient data
never gets to call itself a market value.
Regel 06.45-06.49: every run records its inputs/model version/confidence/
warnings, is versioned, and a new inspection creates a new run rather than
overwriting the old one (append-only, exactly like DataPoint).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin, utcnow


class ValuationRun(UUIDPKMixin, Base):
    __tablename__ = "valuation_runs"

    unit_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("units.id"), nullable=True)
    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)

    valuation_date: Mapped[date] = mapped_column(Date, nullable=False)  # Stichtag, Regel 06.11
    model_version_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("model_versions.id"), nullable=True)

    # Regel 06.32-06.33.
    value_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MARKET_VALUE | INDICATIVE_VALUE

    as_is_low_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    as_is_base_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    as_is_high_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    central_value_method: Mapped[str] = mapped_column(String(100), nullable=False)  # Regel 06.21-06.22

    confidence_score: Mapped[object] = mapped_column(Numeric(6, 4), nullable=False)
    confidence_breakdown: Mapped[dict] = mapped_column(JSONVariant, nullable=False)

    warnings: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)

    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    recorded_by: Mapped[str] = mapped_column(String(200), nullable=False)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. INITIAL, NEW_INSPECTION, NEW_COMPARABLES

    # Regel 06.48-06.49, C.19: append-only; a new run never overwrites an
    # old one, it supersedes it via this link.
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    supersedes_run_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("valuation_runs.id"), nullable=True)

    method_results: Mapped[list["ValuationMethodResult"]] = relationship(back_populates="valuation_run")


class ValuationMethodResult(UUIDPKMixin, Base):
    """Regel 06.1-06.2, 06.34-06.38: which method(s) fed a run, each with
    its own range and data-quality note; disagreement between methods
    must stay visible rather than being merged away silently."""

    __tablename__ = "valuation_method_results"

    valuation_run_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("valuation_runs.id"), nullable=False)
    method_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value_low_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    value_base_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    value_high_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_used: Mapped[object] = mapped_column(Numeric(6, 4), nullable=False)
    data_quality_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    comparable_set_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("comparable_sets.id"), nullable=True)

    valuation_run: Mapped[ValuationRun] = relationship(back_populates="method_results")
