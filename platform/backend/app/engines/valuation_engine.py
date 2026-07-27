"""Engine 06 - Valuation, plus the Teil E AS-IS discount formulas.

Regel 06.19-06.20: no false precision - the AS_IS range widens as
confidence drops, it never stays a fixed-width band regardless of data
quality.
Regel 06.32-06.33: MARKET_VALUE requires a minimum confidence; below that
the run is only ever an INDICATIVE_VALUE.
Regel C.47-C.48: if there isn't enough comparable data to produce a range
at all, the engine refuses (NOT_RELIABLY_DETERMINABLE) rather than
inventing a number.
Teil E: AS_IS_DISCOUNT_EUR / AS_IS_DISCOUNT_PERCENT, and the
MARKET_UNDERVALUE vs. INDICATIVE_DISCOUNT distinction.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.confidence import ConfidenceResult
from app.engines.comparable_engine import ComparableSummary
from app.models.valuation import ValuationRun, ValuationMethodResult

MIN_CONFIDENCE_FOR_MARKET_VALUE_SCREENING_DEFAULT = Decimal("0.55")


class InsufficientDataForValuation(Exception):
    """Regel C.47-C.48: raised instead of fabricating a plausible-looking
    number when there simply isn't enough comparable data."""


def range_widening_factor(confidence: Decimal, *, min_spread: Decimal = Decimal("0.05"), max_spread: Decimal = Decimal("0.45")) -> Decimal:
    """Regel 06.20: lower confidence -> wider AS_IS range."""
    spread = min_spread + (Decimal("1") - confidence) * (max_spread - min_spread)
    return max(min_spread, min(max_spread, spread)).quantize(Decimal("0.0001"))


def determine_value_type(confidence: Decimal, min_confidence: Decimal = MIN_CONFIDENCE_FOR_MARKET_VALUE_SCREENING_DEFAULT) -> str:
    """Regel 06.32-06.33."""
    return "MARKET_VALUE" if confidence >= min_confidence else "INDICATIVE_VALUE"


def _get_current_run(session: Session, *, unit_id: uuid.UUID | None, property_id: uuid.UUID | None) -> ValuationRun | None:
    stmt = select(ValuationRun).where(ValuationRun.is_current.is_(True))
    if unit_id is not None:
        stmt = stmt.where(ValuationRun.unit_id == unit_id)
    if property_id is not None:
        stmt = stmt.where(ValuationRun.property_id == property_id)
    return session.scalars(stmt).one_or_none()


def create_valuation_run(
    session: Session,
    *,
    unit_id: uuid.UUID | None,
    property_id: uuid.UUID | None,
    valuation_date: date,
    comparable_summary: ComparableSummary,
    living_area_sqm: Decimal,
    confidence_result: ConfidenceResult,
    recorded_by: str,
    trigger: str,
    comparable_set_id: uuid.UUID | None = None,
    model_version_id: uuid.UUID | None = None,
) -> ValuationRun:
    base_price_per_sqm = comparable_summary.weighted_median or comparable_summary.median
    if base_price_per_sqm is None:
        raise InsufficientDataForValuation(
            "Keine belastbaren Vergleichspreise vorhanden - Wert ist NOT_RELIABLY_DETERMINABLE, "
            "nicht schätzbar (Regel C.47-C.48)."
        )
    if living_area_sqm is None or living_area_sqm <= 0:
        raise InsufficientDataForValuation("Wohnfläche unbekannt oder ungültig - Bewertung nicht möglich.")

    base_value_eur = (base_price_per_sqm * living_area_sqm).quantize(Decimal("0.01"))
    base_value_cents = int(base_value_eur * 100)

    widen = range_widening_factor(confidence_result.score)
    low_cents = int((base_value_eur * (Decimal("1") - widen) * 100).quantize(Decimal("1")))
    high_cents = int((base_value_eur * (Decimal("1") + widen) * 100).quantize(Decimal("1")))

    value_type = determine_value_type(confidence_result.score)

    warnings: list[str] = list(comparable_summary.warnings)
    if value_type == "INDICATIVE_VALUE":
        warnings.append(
            f"Confidence {confidence_result.score} unter Schwelle "
            f"{MIN_CONFIDENCE_FOR_MARKET_VALUE_SCREENING_DEFAULT} - als INDICATIVE_VALUE ausgegeben (Regel 06.33)."
        )

    previous = _get_current_run(session, unit_id=unit_id, property_id=property_id)

    run = ValuationRun(
        unit_id=unit_id,
        property_id=property_id,
        valuation_date=valuation_date,
        model_version_id=model_version_id,
        value_type=value_type,
        as_is_low_cents=low_cents,
        as_is_base_cents=base_value_cents,
        as_is_high_cents=high_cents,
        central_value_method=(
            f"gewichteter Median €/m² aus SOLD_COMPARABLE ({comparable_summary.n_included} Objekte) "
            f"× verifizierte/beste verfügbare Wohnfläche; Spannbreite ±{widen * 100}% je nach Confidence."
        ),
        confidence_score=confidence_result.score,
        confidence_breakdown={
            "breakdown": {k: str(v) for k, v in confidence_result.breakdown.items()},
            "weights_used": {k: str(v) for k, v in confidence_result.weights_used.items()},
            "capped": confidence_result.capped,
            "cap_reason": confidence_result.cap_reason,
        },
        warnings=warnings,
        recorded_at=datetime.now(timezone.utc),
        recorded_by=recorded_by,
        trigger=trigger,
        is_current=True,
        supersedes_run_id=previous.id if previous else None,
    )
    session.add(run)
    session.flush()

    session.add(
        ValuationMethodResult(
            valuation_run_id=run.id,
            method_name="COMPARABLE_SALES",
            value_low_cents=low_cents,
            value_base_cents=base_value_cents,
            value_high_cents=high_cents,
            weight_used=Decimal("1.0"),
            data_quality_notes="; ".join(warnings) if warnings else None,
            comparable_set_id=comparable_set_id,
        )
    )

    if previous is not None:
        previous.is_current = False

    session.flush()
    return run


def as_is_discount(asking_price_cents: int, valuation_run: ValuationRun) -> dict:
    """Teil E:
    AS_IS_DISCOUNT_EUR = AS_IS_VALUE_BASE - ASKING_PRICE
    AS_IS_DISCOUNT_PERCENT = (AS_IS_VALUE_BASE - ASKING_PRICE) / AS_IS_VALUE_BASE * 100

    Only labeled MARKET_UNDERVALUE when the underlying valuation is a
    MARKET_VALUE; otherwise it is an INDICATIVE_DISCOUNT (Teil E, Regel
    C.15-C.16: data quality and economic attractiveness are separate axes).
    """
    base_cents = valuation_run.as_is_base_cents
    discount_cents = base_cents - asking_price_cents
    discount_percent = (
        (Decimal(discount_cents) / Decimal(base_cents) * Decimal(100)).quantize(Decimal("0.01"))
        if base_cents != 0
        else None
    )
    label = "MARKET_UNDERVALUE" if valuation_run.value_type == "MARKET_VALUE" else "INDICATIVE_DISCOUNT"
    return {
        "as_is_discount_cents": discount_cents,
        "as_is_discount_percent": discount_percent,
        "label": label,
        "value_type": valuation_run.value_type,
        "confidence_score": valuation_run.confidence_score,
    }
