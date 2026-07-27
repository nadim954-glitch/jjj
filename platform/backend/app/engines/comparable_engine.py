"""Engine 05 - Comparable & Market Data.

Regel 05.1-05.5: SOLD_COMPARABLE / ASKING_COMPARABLE / OFFICIAL_AGGREGATE
are never mixed into one unlabeled average.
Regel 05.31-05.35: similarity is a transparent, configurable, per-dimension
breakdown - explicitly a product parameter, not a proven scientific model
until empirically calibrated (Regel 05.35).
Regel 05.36-05.41: median/quartiles/outlier detection; outliers are
flagged with a reason and never deleted.
Regel 05.42-05.49: minimum data quality gates and explicit inclusion/
exclusion reasoning for every comparable.
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from app.core.enums import ComparableClass
from app.models.market import Comparable, ComparableSet


@dataclass(frozen=True, slots=True)
class SimilarityWeights:
    """Regel 05.34-05.35: a product parameter, explicitly not a proven
    scientific model unless/until empirically calibrated against
    realized outcomes (Engine 20)."""

    distance: Decimal = Decimal("0.30")
    time: Decimal = Decimal("0.15")
    size: Decimal = Decimal("0.25")
    condition: Decimal = Decimal("0.15")
    year_built: Decimal = Decimal("0.10")
    features: Decimal = Decimal("0.05")

    def total(self) -> Decimal:
        return self.distance + self.time + self.size + self.condition + self.year_built + self.features


DEFAULT_WEIGHTS_SCREENING_DEFAULT = SimilarityWeights()

# Coarse ordering for a partial-credit condition comparison. Anything not
# in this list contributes an UNKNOWN (None) condition score, not a
# fabricated middle value.
_CONDITION_ORDER = [
    "ENTKERNT",
    "SANIERUNGSBEDUERFTIG",
    "RENOVIERUNGSBEDUERFTIG",
    "GEPFLEGT",
    "MODERNISIERT",
    "SANIERT",
    "NEUWERTIG",
    "NEUBAU",
]


@dataclass(frozen=True, slots=True)
class SubjectProfile:
    reference_date: date
    living_area_sqm: Decimal | None = None
    year_built: int | None = None
    condition_label: str | None = None
    features: dict[str, bool] = field(default_factory=dict)
    max_radius_km: Decimal = Decimal("3.0")
    max_time_window_months: int = 24
    size_tolerance_pct: Decimal = Decimal("0.20")
    year_tolerance_years: int = 15


def _months_between(a: date, b: date) -> Decimal:
    days = abs((a - b).days)
    return (Decimal(days) / Decimal("30.44")).quantize(Decimal("0.01"))


def _bounded_score(distance: Decimal, max_distance: Decimal) -> Decimal | None:
    if max_distance <= 0:
        return None
    if distance < 0:
        distance = -distance
    if distance >= max_distance:
        return Decimal("0")
    return (Decimal("1") - distance / max_distance).quantize(Decimal("0.0001"))


def _condition_score(subject_label: str | None, comp_label: str | None) -> Decimal | None:
    if not subject_label or not comp_label:
        return None
    subject_label = subject_label.upper()
    comp_label = comp_label.upper()
    if subject_label not in _CONDITION_ORDER or comp_label not in _CONDITION_ORDER:
        return Decimal("1") if subject_label == comp_label else None
    idx_a = _CONDITION_ORDER.index(subject_label)
    idx_b = _CONDITION_ORDER.index(comp_label)
    span = len(_CONDITION_ORDER) - 1
    return (Decimal("1") - Decimal(abs(idx_a - idx_b)) / Decimal(span)).quantize(Decimal("0.0001"))


def _features_score(subject_features: dict[str, bool], comp_features: dict | None) -> Decimal | None:
    comp_features = comp_features or {}
    keys = set(subject_features) & set(comp_features)
    if not keys:
        return None
    matches = sum(1 for k in keys if bool(subject_features[k]) == bool(comp_features[k]))
    return (Decimal(matches) / Decimal(len(keys))).quantize(Decimal("0.0001"))


def compute_similarity(
    comparable: Comparable,
    subject: SubjectProfile,
    weights: SimilarityWeights = DEFAULT_WEIGHTS_SCREENING_DEFAULT,
) -> tuple[dict[str, Decimal | None], Decimal]:
    """Returns (per-dimension breakdown, weighted total).

    Missing dimensions (None) are excluded from both the weighted sum and
    the weight normalization - they do not silently count as a match.
    """
    breakdown: dict[str, Decimal | None] = {}

    breakdown["distance"] = (
        _bounded_score(comparable.distance_km, subject.max_radius_km)
        if comparable.distance_km is not None
        else None
    )

    time_delta = _months_between(comparable.reference_date, subject.reference_date)
    breakdown["time"] = _bounded_score(time_delta, Decimal(subject.max_time_window_months))

    if comparable.living_area_sqm is not None and subject.living_area_sqm is not None and subject.living_area_sqm > 0:
        diff_pct = abs(comparable.living_area_sqm - subject.living_area_sqm) / subject.living_area_sqm
        breakdown["size"] = (
            None
            if diff_pct >= subject.size_tolerance_pct
            else (Decimal("1") - diff_pct / subject.size_tolerance_pct).quantize(Decimal("0.0001"))
        )
    else:
        breakdown["size"] = None

    breakdown["condition"] = _condition_score(subject.condition_label, comparable.condition_label)

    if comparable.year_built is not None and subject.year_built is not None:
        year_diff = abs(comparable.year_built - subject.year_built)
        breakdown["year_built"] = (
            None
            if year_diff >= subject.year_tolerance_years
            else (Decimal("1") - Decimal(year_diff) / Decimal(subject.year_tolerance_years)).quantize(
                Decimal("0.0001")
            )
        )
    else:
        breakdown["year_built"] = None

    breakdown["features"] = _features_score(subject.features, comparable.features)

    weight_map = {
        "distance": weights.distance,
        "time": weights.time,
        "size": weights.size,
        "condition": weights.condition,
        "year_built": weights.year_built,
        "features": weights.features,
    }
    usable = {k: v for k, v in breakdown.items() if v is not None}
    if not usable:
        return breakdown, Decimal("0")
    total_weight = sum(weight_map[k] for k in usable)
    total = sum(usable[k] * weight_map[k] for k in usable) / total_weight
    return breakdown, total.quantize(Decimal("0.0001"))


def filter_by_class(comparables: list[Comparable], allowed: list[ComparableClass]) -> list[Comparable]:
    """Regel 05.1-05.5: the ONLY sanctioned way to select a subset for a
    calculation - never filter comparables ad hoc elsewhere."""
    return [c for c in comparables if c.comparable_class in allowed and not c.excluded]


def price_per_sqm(comparable: Comparable) -> Decimal | None:
    if comparable.living_area_sqm is None or comparable.living_area_sqm == 0:
        return None
    return (Decimal(comparable.price_cents) / Decimal(100) / comparable.living_area_sqm).quantize(Decimal("0.01"))


def quartiles(values: list[Decimal]) -> tuple[Decimal, Decimal, Decimal]:
    """Returns (Q1, median, Q3) using linear interpolation, all Decimal."""
    ordered = sorted(values)
    floats = [float(v) for v in ordered]
    q1, med, q3 = statistics.quantiles(floats, n=4, method="inclusive")[0:3] if len(floats) >= 2 else (
        floats[0],
        floats[0],
        floats[0],
    )
    return (
        Decimal(str(round(q1, 2))),
        Decimal(str(round(med, 2))),
        Decimal(str(round(q3, 2))),
    )


def weighted_median(value_weight_pairs: list[tuple[Decimal, Decimal]]) -> Decimal | None:
    pairs = sorted(value_weight_pairs, key=lambda p: p[0])
    total_weight = sum(w for _, w in pairs)
    if total_weight <= 0:
        return None
    cumulative = Decimal("0")
    half = total_weight / 2
    for value, weight in pairs:
        cumulative += weight
        if cumulative >= half:
            return value
    return pairs[-1][0]


def detect_outliers_iqr(comparables: list[Comparable], k: Decimal = Decimal("1.5")) -> list[Comparable]:
    """Regel 05.38-05.41: flag, never delete; the reason is always stated
    so a high price cannot be quietly removed just because it hurts the
    thesis (Regel 05.41)."""
    priced = [(c, price_per_sqm(c)) for c in comparables]
    known = [p for _, p in priced if p is not None]
    if len(known) < 4:
        return comparables
    q1, _, q3 = quartiles(known)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    flagged: list[Comparable] = []
    for comp, ppsqm in priced:
        if ppsqm is None:
            continue
        if ppsqm < lower or ppsqm > upper:
            comp.is_outlier = True
            comp.outlier_reason = (
                f"€/m² {ppsqm} liegt außerhalb [{lower:.2f}, {upper:.2f}] (IQR-Regel, k={k}); "
                f"Q1={q1}, Q3={q3}. Nicht automatisch entfernt (Regel 05.39)."
            )
            flagged.append(comp)
    return flagged


def log_expansion(comparable_set: ComparableSet, *, new_radius_km: Decimal | None, new_time_window_months: int | None,
                   reason: str, resulting_count: int) -> None:
    """Regel 05.12-05.13: every radius/time-window expansion is logged."""
    entry = {
        "previous_radius_km": str(comparable_set.search_radius_km_final),
        "previous_time_window_months": comparable_set.time_window_months_final,
        "new_radius_km": str(new_radius_km) if new_radius_km is not None else None,
        "new_time_window_months": new_time_window_months,
        "reason": reason,
        "resulting_count": resulting_count,
    }
    log = list(comparable_set.expansion_log or [])
    log.append(entry)
    comparable_set.expansion_log = log
    if new_radius_km is not None:
        comparable_set.search_radius_km_final = new_radius_km
    if new_time_window_months is not None:
        comparable_set.time_window_months_final = new_time_window_months


MIN_SOLD_COMPARABLES_FOR_RELIABLE = 5


@dataclass(frozen=True, slots=True)
class ComparableSummary:
    comparable_class: ComparableClass
    n_included: int
    n_excluded: int
    n_outliers: int
    q1: Decimal | None
    median: Decimal | None
    q3: Decimal | None
    weighted_median: Decimal | None
    warnings: list[str]


def summarize_class(
    comparable_set: ComparableSet,
    comparable_class: ComparableClass,
    subject: SubjectProfile | None = None,
    weights: SimilarityWeights = DEFAULT_WEIGHTS_SCREENING_DEFAULT,
) -> ComparableSummary:
    all_of_class = [c for c in comparable_set.comparables if c.comparable_class == comparable_class]
    included = [c for c in all_of_class if not c.excluded]
    excluded = [c for c in all_of_class if c.excluded]

    priced = [(c, price_per_sqm(c)) for c in included]
    known_prices = [p for _, p in priced if p is not None]

    outliers = [c for c in included if c.is_outlier]

    warnings: list[str] = []
    if comparable_class == ComparableClass.SOLD_COMPARABLE and len(known_prices) < MIN_SOLD_COMPARABLES_FOR_RELIABLE:
        warnings.append(
            f"Nur {len(known_prices)} belegte Kauffälle (Mindestanforderung "
            f"{MIN_SOLD_COMPARABLES_FOR_RELIABLE}) - Confidence ist entsprechend reduziert (Regel 05.43)."
        )

    q1 = med = q3 = wmed = None
    if known_prices:
        q1, med, q3 = quartiles(known_prices)
        if subject is not None:
            weighted_pairs = []
            for comp, price in priced:
                if price is None:
                    continue
                _, sim_total = compute_similarity(comp, subject, weights)
                weighted_pairs.append((price, sim_total if sim_total > 0 else Decimal("0.0001")))
            wmed = weighted_median(weighted_pairs)

    return ComparableSummary(
        comparable_class=comparable_class,
        n_included=len(included),
        n_excluded=len(excluded),
        n_outliers=len(outliers),
        q1=q1,
        median=med,
        q3=q3,
        weighted_median=wmed,
        warnings=warnings,
    )
