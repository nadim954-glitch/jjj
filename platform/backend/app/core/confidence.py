"""Confidence scoring per Engine 03 (Regel 03.31-03.47).

Regel 03.33: Source Quality and Data Confidence are distinct metrics -
this module only computes the latter. Regel 03.43-03.44: confidence must
be rule-based (source quality, completeness, recency, consistency,
comparability), never a bare LLM self-rating. Regel 03.45: the weights
below are a PRODUCT PARAMETER, not a market law - they live in
InvestmentPolicy-style config, not as an implicit "fact".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


# Regel 03.45: explicitly labelled as a product default, not a market law.
DEFAULT_CONFIDENCE_WEIGHTS_SCREENING_DEFAULT: dict[str, Decimal] = {
    "source_quality": Decimal("0.30"),
    "completeness": Decimal("0.25"),
    "recency": Decimal("0.15"),
    "consistency": Decimal("0.20"),
    "comparability": Decimal("0.10"),
}


@dataclass(frozen=True, slots=True)
class ConfidenceInputs:
    """Each factor is a 0..1 score computed by the calling engine from
    concrete, inspectable evidence - never guessed."""

    source_quality: Decimal
    completeness: Decimal
    recency: Decimal
    consistency: Decimal
    comparability: Decimal
    # Regel 03.47: a hard ceiling imposed when critical primary data is
    # missing, regardless of how the weighted factors compute.
    max_confidence_cap: Decimal | None = None
    cap_reason: str | None = None


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    score: Decimal  # 0..1
    breakdown: dict[str, Decimal]
    weights_used: dict[str, Decimal]
    capped: bool
    cap_reason: str | None


def compute_confidence(
    inputs: ConfidenceInputs,
    weights: dict[str, Decimal] | None = None,
) -> ConfidenceResult:
    """Regel 03.46: result must be explorable ('aufklappbar begründet')."""
    w = weights or DEFAULT_CONFIDENCE_WEIGHTS_SCREENING_DEFAULT
    factors = {
        "source_quality": inputs.source_quality,
        "completeness": inputs.completeness,
        "recency": inputs.recency,
        "consistency": inputs.consistency,
        "comparability": inputs.comparability,
    }
    for name, value in factors.items():
        if not (Decimal("0") <= value <= Decimal("1")):
            raise ValueError(f"confidence factor {name}={value} out of range [0,1]")

    breakdown = {name: (value * w[name]) for name, value in factors.items()}
    raw_score = sum(breakdown.values(), Decimal("0"))

    capped = False
    cap_reason = None
    score = raw_score
    if inputs.max_confidence_cap is not None and raw_score > inputs.max_confidence_cap:
        score = inputs.max_confidence_cap
        capped = True
        cap_reason = inputs.cap_reason

    return ConfidenceResult(
        score=score.quantize(Decimal("0.0001")),
        breakdown={k: v.quantize(Decimal("0.0001")) for k, v in breakdown.items()},
        weights_used=dict(w),
        capped=capped,
        cap_reason=cap_reason,
    )


def confidence_band(score: Decimal) -> str:
    """A coarse label for UI use. Never used as a substitute for the
    numeric score + breakdown (Regel 03.46)."""
    if score >= Decimal("0.75"):
        return "HIGH"
    if score >= Decimal("0.5"):
        return "MEDIUM"
    if score >= Decimal("0.25"):
        return "LOW"
    return "VERY_LOW"
