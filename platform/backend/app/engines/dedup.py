"""Engine 02 - Property Identity & Normalization: dedup/merge logic.

Regel 02.17-02.20: similarity combines address, area, rooms, price and
description; a single matching feature is never sufficient; the engine
produces a probability, and merges above a "confirm" threshold require
explicit confirmation rather than happening silently.
Regel 02.21-02.23: merges are reversible, logged, and merging two listings
into one Property must never drop either listing or its price history -
`Listing.property_id` is the only thing that changes.
"""
from __future__ import annotations

import difflib
import uuid
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.listing import Listing
from app.models.property_ import Property


# Regel 02.18: no single feature may drive an automatic merge. A merge
# may only be auto-suggested (still requiring confirm_merge) when at
# least this many individual features score above STRONG_MATCH_THRESHOLD.
STRONG_MATCH_THRESHOLD = Decimal("0.85")
MIN_STRONG_FEATURES_FOR_SUGGESTION = 2
# Below this combined score we don't even suggest a candidate.
MIN_COMBINED_SCORE_TO_SUGGEST = Decimal("0.55")

_FEATURE_WEIGHTS = {
    "address": Decimal("0.45"),
    "area": Decimal("0.25"),
    "rooms": Decimal("0.10"),
    "price": Decimal("0.10"),
    "description": Decimal("0.10"),
}


@dataclass(frozen=True, slots=True)
class MergeCandidate:
    listing_a_id: uuid.UUID
    listing_b_id: uuid.UUID
    feature_scores: dict[str, Decimal]
    strong_features: list[str]
    combined_score: Decimal
    suggested: bool
    reasons: list[str]


def _text_similarity(a: str | None, b: str | None) -> Decimal | None:
    if not a or not b:
        return None
    ratio = difflib.SequenceMatcher(None, a.strip().lower(), b.strip().lower()).ratio()
    return Decimal(str(round(ratio, 4)))


def _numeric_closeness(a: Decimal | None, b: Decimal | None, tolerance_pct: Decimal) -> Decimal | None:
    if a is None or b is None:
        return None
    if a == 0 and b == 0:
        return Decimal("1")
    base = max(abs(a), abs(b))
    if base == 0:
        return Decimal("1")
    diff_pct = abs(a - b) / base
    if diff_pct >= tolerance_pct:
        return Decimal("0")
    return (Decimal("1") - diff_pct / tolerance_pct).quantize(Decimal("0.0001"))


def _naive_utc(value):
    """SQLite loses tzinfo for a snapshot reloaded fresh from the DB
    (vs. one still held aware in the session's identity map) - normalize
    before comparing so sort order doesn't depend on cache state."""
    if value.tzinfo is not None:
        from datetime import timezone

        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def _latest_snapshot(listing: Listing):
    if not listing.snapshots:
        return None
    return sorted(listing.snapshots, key=lambda s: _naive_utc(s.captured_at))[-1]


def score_similarity(listing_a: Listing, listing_b: Listing) -> MergeCandidate:
    snap_a = _latest_snapshot(listing_a)
    snap_b = _latest_snapshot(listing_b)

    scores: dict[str, Decimal] = {}
    reasons: list[str] = []

    addr_score = _text_similarity(listing_a.raw_address_text, listing_b.raw_address_text)
    if addr_score is not None:
        scores["address"] = addr_score
        reasons.append(f"Adresstext-Ähnlichkeit: {addr_score}")

    if snap_a is not None and snap_b is not None:
        area_score = _numeric_closeness(
            snap_a.living_area_listing_sqm, snap_b.living_area_listing_sqm, Decimal("0.05")
        )
        if area_score is not None:
            scores["area"] = area_score
            reasons.append(f"Flächen-Ähnlichkeit: {area_score}")

        rooms_score = _numeric_closeness(snap_a.rooms_claimed, snap_b.rooms_claimed, Decimal("0.15"))
        if rooms_score is not None:
            scores["rooms"] = rooms_score

        # Regel 02.23: price similarity is only a weak supporting signal -
        # different prices for the same object must remain plausible
        # (different point in time, negotiation, etc.), so a mismatch
        # here never blocks a merge by itself.
        if snap_a.asking_price_cents is not None and snap_b.asking_price_cents is not None:
            price_score = _numeric_closeness(
                Decimal(snap_a.asking_price_cents), Decimal(snap_b.asking_price_cents), Decimal("0.20")
            )
            if price_score is not None:
                scores["price"] = price_score

        desc_score = _text_similarity(snap_a.description_text, snap_b.description_text)
        if desc_score is not None:
            scores["description"] = desc_score

    if not scores:
        return MergeCandidate(
            listing_a_id=listing_a.id,
            listing_b_id=listing_b.id,
            feature_scores={},
            strong_features=[],
            combined_score=Decimal("0"),
            suggested=False,
            reasons=["Keine vergleichbaren Merkmale vorhanden."],
        )

    total_weight = sum(_FEATURE_WEIGHTS[f] for f in scores)
    combined = sum(scores[f] * _FEATURE_WEIGHTS[f] for f in scores) / total_weight
    combined = combined.quantize(Decimal("0.0001"))

    strong_features = [f for f, s in scores.items() if s >= STRONG_MATCH_THRESHOLD]

    # Regel 02.18: never suggest a merge off a single strong feature alone.
    suggested = (
        combined >= MIN_COMBINED_SCORE_TO_SUGGEST and len(strong_features) >= MIN_STRONG_FEATURES_FOR_SUGGESTION
    )

    return MergeCandidate(
        listing_a_id=listing_a.id,
        listing_b_id=listing_b.id,
        feature_scores=scores,
        strong_features=strong_features,
        combined_score=combined,
        suggested=suggested,
        reasons=reasons,
    )


class MergeNotJustifiedError(Exception):
    pass


def confirm_merge(
    session: Session,
    *,
    listing_a: Listing,
    listing_b: Listing,
    candidate: MergeCandidate,
    performed_by: str,
    target_property: Property | None = None,
    override_single_feature: bool = False,
) -> Property:
    """Regel 02.19-02.22: explicit, logged confirmation step.

    Never called implicitly by scoring. If neither listing has strength
    in >=2 features, a human must pass override_single_feature=True and
    the override is itself logged - this keeps Regel 02.18 enforceable
    while still allowing a human who has out-of-band certainty (e.g. they
    personally recognize the unit) to proceed.
    """
    if not override_single_feature and len(candidate.strong_features) < MIN_STRONG_FEATURES_FOR_SUGGESTION:
        raise MergeNotJustifiedError(
            "Regel 02.18: weniger als zwei starke Übereinstimmungsmerkmale - "
            "Zusammenführung erfordert override_single_feature=True mit Begründung."
        )

    if target_property is None:
        target_property = listing_a.property_id and listing_a.property
        if target_property is None:
            target_property = listing_b.property_id and listing_b.property
    if target_property is None:
        raise ValueError("Keine Ziel-Property vorhanden oder ableitbar - bitte explizit angeben.")

    previous_property_a = listing_a.property_id
    previous_property_b = listing_b.property_id

    listing_a.property_id = target_property.id
    listing_b.property_id = target_property.id

    session.add(
        AuditLog(
            entity_type="Property",
            entity_id=target_property.id,
            action="MERGE_LISTINGS",
            summary=(
                f"Listings {listing_a.id} und {listing_b.id} zu Property {target_property.id} "
                f"zusammengeführt (Score {candidate.combined_score}, "
                f"starke Merkmale: {candidate.strong_features})."
            ),
            payload={
                "listing_a_id": str(listing_a.id),
                "listing_b_id": str(listing_b.id),
                "previous_property_a": str(previous_property_a) if previous_property_a else None,
                "previous_property_b": str(previous_property_b) if previous_property_b else None,
                "feature_scores": {k: str(v) for k, v in candidate.feature_scores.items()},
                "combined_score": str(candidate.combined_score),
                "override_single_feature": override_single_feature,
            },
            performed_by=performed_by,
        )
    )
    session.flush()
    return target_property


def unmerge(session: Session, *, listing: Listing, performed_by: str, reason: str) -> None:
    """Regel 02.21: incorrectly merged objects must be separable again."""
    previous_property_id = listing.property_id
    listing.property_id = None
    session.add(
        AuditLog(
            entity_type="Listing",
            entity_id=listing.id,
            action="UNMERGE_LISTING",
            summary=f"Listing {listing.id} von Property {previous_property_id} getrennt: {reason}",
            payload={"previous_property_id": str(previous_property_id) if previous_property_id else None},
            performed_by=performed_by,
        )
    )
    session.flush()
