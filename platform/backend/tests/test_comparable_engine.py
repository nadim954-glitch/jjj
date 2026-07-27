"""Engine 05 tests: Regel 05.1-05.5 (class separation, Test J.2),
05.21-05.22 (condition adjustment, Test J.1), 05.38-05.43 (outliers never
deleted, minimum sample confidence warning)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.enums import ComparableClass
from app.engines.comparable_engine import (
    MIN_SOLD_COMPARABLES_FOR_RELIABLE,
    SubjectProfile,
    compute_similarity,
    detect_outliers_iqr,
    summarize_class,
)
from app.models.market import Comparable, ComparableSet
from app.models.source import SourceRecord


def _source_record(session, transaction_source) -> SourceRecord:
    rec = SourceRecord(
        source_id=transaction_source.id,
        retrieved_at=datetime.now(timezone.utc),
        import_method="MANUAL",
    )
    session.add(rec)
    session.flush()
    return rec


def _make_set(session) -> ComparableSet:
    cs = ComparableSet(
        search_radius_km_initial=Decimal("1.0"),
        search_radius_km_final=Decimal("1.0"),
        time_window_months_initial=12,
        time_window_months_final=12,
    )
    session.add(cs)
    session.flush()
    return cs


def _comp(session, cs, source_record, *, price_eur, area, condition, ref_date, klass, distance_km=Decimal("0.5")):
    c = Comparable(
        comparable_set_id=cs.id,
        comparable_class=klass,
        source_record_id=source_record.id,
        price_cents=int(Decimal(price_eur) * 100),
        reference_date=ref_date,
        living_area_sqm=Decimal(area),
        condition_label=condition,
        distance_km=distance_km,
    )
    session.add(c)
    session.flush()
    return c


def test_condition_mismatch_reduces_similarity_not_equated(session, transaction_source):
    """Test J.1: a fully renovated 6.000 EUR/m2 comparable must not be
    equated with an unrenovated subject just because size/location match."""
    cs = _make_set(session)
    rec = _source_record(session, transaction_source)

    renovated_comp = _comp(
        session, cs, rec, price_eur="480000", area="80", condition="SANIERT",
        ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE,
    )
    matching_comp = _comp(
        session, cs, rec, price_eur="300000", area="80", condition="SANIERUNGSBEDUERFTIG",
        ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE,
    )

    subject = SubjectProfile(reference_date=date(2026, 1, 1), living_area_sqm=Decimal("80"), condition_label="SANIERUNGSBEDUERFTIG")

    _, sim_renovated = compute_similarity(renovated_comp, subject)
    _, sim_matching = compute_similarity(matching_comp, subject)

    assert sim_matching > sim_renovated  # the condition mismatch must be visible in the score
    breakdown_renovated, _ = compute_similarity(renovated_comp, subject)
    assert breakdown_renovated["condition"] is not None
    assert breakdown_renovated["condition"] < Decimal("1.0")


def test_asking_comparables_never_enter_sold_median(session, transaction_source):
    """Test J.2: five current portal listings must not be treated as five
    completed sales."""
    cs = _make_set(session)
    rec = _source_record(session, transaction_source)

    for i in range(5):
        _comp(
            session, cs, rec, price_eur=str(900000 + i * 1000), area="100", condition="GEPFLEGT",
            ref_date=date(2026, 1, 1), klass=ComparableClass.ASKING_COMPARABLE,
        )
    # only one real sale, at a much lower price
    _comp(
        session, cs, rec, price_eur="300000", area="100", condition="GEPFLEGT",
        ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE,
    )
    session.commit()

    summary = summarize_class(cs, ComparableClass.SOLD_COMPARABLE)
    assert summary.n_included == 1
    assert summary.median == Decimal("3000.00")  # 300000 / 100 sqm, not pulled toward the 900k asking prices
    assert any("Kauffälle" in w for w in summary.warnings)


def test_outliers_are_flagged_never_removed(session, transaction_source):
    cs = _make_set(session)
    rec = _source_record(session, transaction_source)

    normal_prices = ["300000", "310000", "295000", "305000"]
    comps = [
        _comp(session, cs, rec, price_eur=p, area="100", condition="GEPFLEGT", ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE)
        for p in normal_prices
    ]
    outlier = _comp(
        session, cs, rec, price_eur="1500000", area="100", condition="GEPFLEGT",
        ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE,
    )
    session.commit()

    flagged = detect_outliers_iqr(cs.comparables)
    assert outlier in flagged
    assert outlier.is_outlier is True
    assert outlier.outlier_reason is not None
    # never deleted / excluded automatically:
    assert outlier.excluded is False
    summary = summarize_class(cs, ComparableClass.SOLD_COMPARABLE)
    assert summary.n_included == 5
    assert summary.n_outliers == 1


def test_min_sample_warning_below_threshold(session, transaction_source):
    cs = _make_set(session)
    rec = _source_record(session, transaction_source)
    _comp(session, cs, rec, price_eur="300000", area="100", condition="GEPFLEGT", ref_date=date(2026, 1, 1), klass=ComparableClass.SOLD_COMPARABLE)
    session.commit()

    summary = summarize_class(cs, ComparableClass.SOLD_COMPARABLE)
    assert summary.n_included < MIN_SOLD_COMPARABLES_FOR_RELIABLE
    assert summary.warnings
