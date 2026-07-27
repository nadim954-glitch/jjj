"""Engine 06 tests: Regel 06.17-06.20 (range widens with confidence),
06.32-06.33 (MARKET_VALUE vs INDICATIVE_VALUE), 06.48-06.49/C.19-C.20
(append-only versioning), C.47-C.48 (refuse rather than fabricate),
Teil E (AS_IS discount / MARKET_UNDERVALUE vs INDICATIVE_DISCOUNT)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.core.confidence import ConfidenceInputs, compute_confidence
from app.engines.comparable_engine import ComparableSummary
from app.engines.valuation_engine import (
    InsufficientDataForValuation,
    as_is_discount,
    create_valuation_run,
    range_widening_factor,
)
from app.core.enums import ComparableClass
from app.models.valuation import ValuationRun


def _confidence(score_inputs: dict):
    return compute_confidence(
        ConfidenceInputs(
            source_quality=score_inputs.get("source_quality", Decimal("0.8")),
            completeness=score_inputs.get("completeness", Decimal("0.8")),
            recency=score_inputs.get("recency", Decimal("0.8")),
            consistency=score_inputs.get("consistency", Decimal("0.8")),
            comparability=score_inputs.get("comparability", Decimal("0.8")),
        )
    )


def _summary(median: Decimal | None, n=6) -> ComparableSummary:
    return ComparableSummary(
        comparable_class=ComparableClass.SOLD_COMPARABLE,
        n_included=n,
        n_excluded=0,
        n_outliers=0,
        q1=median,
        median=median,
        q3=median,
        weighted_median=median,
        warnings=[],
    )


def test_range_widens_as_confidence_drops():
    wide = range_widening_factor(Decimal("0.2"))
    narrow = range_widening_factor(Decimal("0.9"))
    assert wide > narrow


def test_insufficient_data_refuses_rather_than_fabricates(session):
    summary = _summary(median=None)
    with pytest.raises(InsufficientDataForValuation):
        create_valuation_run(
            session,
            unit_id=None,
            property_id=None,
            valuation_date=date(2026, 1, 1),
            comparable_summary=summary,
            living_area_sqm=Decimal("80"),
            confidence_result=_confidence({}),
            recorded_by="tester",
            trigger="INITIAL",
        )


def test_low_confidence_yields_indicative_value_not_market_value(session, sample_property):
    summary = _summary(median=Decimal("3000.00"))
    low_conf = _confidence(
        {
            "source_quality": Decimal("0.2"),
            "completeness": Decimal("0.2"),
            "recency": Decimal("0.2"),
            "consistency": Decimal("0.2"),
            "comparability": Decimal("0.2"),
        }
    )
    run = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 1, 1),
        comparable_summary=summary,
        living_area_sqm=Decimal("80"),
        confidence_result=low_conf,
        recorded_by="tester",
        trigger="INITIAL",
    )
    session.commit()
    assert run.value_type == "INDICATIVE_VALUE"
    assert run.as_is_low_cents < run.as_is_base_cents < run.as_is_high_cents


def test_high_confidence_yields_market_value(session, sample_property):
    summary = _summary(median=Decimal("3000.00"))
    high_conf = _confidence({})  # defaults to 0.8 across the board
    run = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 1, 1),
        comparable_summary=summary,
        living_area_sqm=Decimal("80"),
        confidence_result=high_conf,
        recorded_by="tester",
        trigger="INITIAL",
    )
    assert run.value_type == "MARKET_VALUE"


def test_new_inspection_supersedes_without_deleting_old_run(session, sample_property):
    summary = _summary(median=Decimal("3000.00"))
    conf = _confidence({})
    run1 = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 1, 1),
        comparable_summary=summary,
        living_area_sqm=Decimal("80"),
        confidence_result=conf,
        recorded_by="tester",
        trigger="INITIAL",
    )
    session.commit()

    summary2 = _summary(median=Decimal("2500.00"))
    run2 = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 6, 1),
        comparable_summary=summary2,
        living_area_sqm=Decimal("80"),
        confidence_result=conf,
        recorded_by="tester",
        trigger="NEW_INSPECTION",
    )
    session.commit()

    session.refresh(run1)
    assert run1.is_current is False
    assert run2.is_current is True
    assert run2.supersedes_run_id == run1.id

    # Regel C.19: the old run must still exist and be queryable, not deleted.
    still_there = session.get(ValuationRun, run1.id)
    assert still_there is not None
    assert still_there.as_is_base_cents == run1.as_is_base_cents


def test_as_is_discount_labels_market_undervalue_only_for_market_value(session, sample_property):
    summary = _summary(median=Decimal("4000.00"))
    conf = _confidence({})  # -> MARKET_VALUE
    run = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 1, 1),
        comparable_summary=summary,
        living_area_sqm=Decimal("80"),
        confidence_result=conf,
        recorded_by="tester",
        trigger="INITIAL",
    )
    # AS_IS_BASE = 4000 * 80 = 320,000 EUR = 32,000,000 cents
    asking_price_cents = 28_000_000  # 280,000 EUR
    result = as_is_discount(asking_price_cents, run)
    assert result["label"] == "MARKET_UNDERVALUE"
    assert result["as_is_discount_cents"] == 4_000_000
    assert result["as_is_discount_percent"] == Decimal("12.50")


def test_as_is_discount_is_indicative_when_confidence_is_low(session, sample_property):
    summary = _summary(median=Decimal("4000.00"))
    low_conf = _confidence(
        {
            "source_quality": Decimal("0.1"),
            "completeness": Decimal("0.1"),
            "recency": Decimal("0.1"),
            "consistency": Decimal("0.1"),
            "comparability": Decimal("0.1"),
        }
    )
    run = create_valuation_run(
        session,
        unit_id=None,
        property_id=sample_property.id,
        valuation_date=date(2026, 1, 1),
        comparable_summary=summary,
        living_area_sqm=Decimal("80"),
        confidence_result=low_conf,
        recorded_by="tester",
        trigger="INITIAL",
    )
    result = as_is_discount(28_000_000, run)
    assert result["label"] == "INDICATIVE_DISCOUNT"
