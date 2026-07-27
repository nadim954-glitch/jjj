"""HTTP API over the implemented engines (Source Registry, Listing Import,
Dedup, Comparable, Valuation - see docs/ENGINE_STATUS.md for what's real
vs. stubbed). Run locally with:

    uvicorn app.api.main:app --reload

This is deliberately a thin layer: every endpoint calls straight into the
engine modules under app/engines/ rather than re-implementing any rule.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.api import schemas
from app.api.deps import get_session
from app.core.enums import DataStatus
from app.engines import dedup as dedup_engine
from app.engines.listing_import import ImportResult, ListingInputRow, import_csv, import_listing, price_history
from app.engines.source_registry import seed_official_sources
from app.engines.valuation_engine import as_is_discount
from app.models.listing import Listing
from app.models.property_ import Property
from app.models.source import Source
from app.models.valuation import ValuationRun

app = FastAPI(
    title="Real Estate Acquisition Intelligence System - API",
    description=(
        "Foundation build (Berlin/Brandenburg). Implemented: Source Registry, "
        "Listing Import, Dedup, Comparable Engine, Valuation Engine. "
        "Everything else is schema-only - see /engine-status."
    ),
    version="0.1.0",
)

MANUAL_SOURCE_NAME = "Manuelle Eingabe / Exposé-Import (URL, PDF, Bild, CSV)"


def _get_manual_source(session: Session) -> Source:
    source = session.query(Source).filter_by(name=MANUAL_SOURCE_NAME).one_or_none()
    if source is None:
        seed_official_sources(session)
        session.commit()
        source = session.query(Source).filter_by(name=MANUAL_SOURCE_NAME).one()
    return source


def _import_result_to_out(result: ImportResult) -> schemas.ImportResultOut:
    return schemas.ImportResultOut(
        listing_id=result.listing.id,
        snapshot_id=result.snapshot.id,
        is_new_listing=result.is_new_listing,
        warnings=result.warnings,
        conflicts=result.conflicts,
    )


@app.get("/engine-status")
def engine_status() -> dict:
    return {
        "implemented": ["source_registry", "listing_import", "dedup", "comparable_engine", "valuation_engine"],
        "stub_schema_only": [
            "condition", "renovation", "water_damage", "weg", "planning_land",
            "rental", "finance", "deal", "risk_due_diligence", "document_intelligence",
            "photo_intelligence", "search_ranking", "ui_deal_room", "learning_calibration",
        ],
        "see": "docs/ENGINE_STATUS.md",
    }


@app.post("/admin/seed-sources", response_model=list[schemas.SourceOut])
def seed_sources(session: Session = Depends(get_session)):
    sources = seed_official_sources(session)
    session.commit()
    return sources


@app.get("/sources", response_model=list[schemas.SourceOut])
def list_sources(session: Session = Depends(get_session)):
    return session.query(Source).order_by(Source.name).all()


@app.post("/listings/manual", response_model=schemas.ImportResultOut)
def create_manual_listing(payload: schemas.ManualListingIn, session: Session = Depends(get_session)):
    source = _get_manual_source(session)
    data = payload.model_dump()
    # Regel C.3/13.8: only claim a concrete status when a concrete value
    # was actually given - never let a default silently overstate certainty.
    data["asking_price_status"] = DataStatus.DOCUMENTED if data.get("asking_price_eur") is not None else DataStatus.UNKNOWN
    data["commission_status"] = DataStatus.DOCUMENTED if data.get("commission_eur") is not None else DataStatus.UNKNOWN
    row = ListingInputRow(**data)
    result = import_listing(session, source=source, row=row, recorded_by="api-user", import_method="MANUAL")
    session.commit()
    return _import_result_to_out(result)


@app.post("/listings/csv", response_model=list[schemas.ImportResultOut])
def create_csv_listings(payload: schemas.CsvImportIn, session: Session = Depends(get_session)):
    source = _get_manual_source(session)
    results = import_csv(
        session, source=source, csv_text=payload.csv_text, recorded_by="api-user", listing_kind=payload.listing_kind
    )
    session.commit()
    return [_import_result_to_out(r) for r in results]


@app.get("/listings/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: uuid.UUID, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, "Listing nicht gefunden")
    return schemas.ListingOut(
        id=listing.id,
        external_listing_id=listing.external_listing_id,
        listing_kind=listing.listing_kind,
        property_type=listing.property_type,
        title=listing.title,
        url=listing.url,
        raw_address_text=listing.raw_address_text,
        is_active=listing.is_active,
        first_seen_at=listing.first_seen_at,
        last_seen_at=listing.last_seen_at,
        property_id=listing.property_id,
        marketing_duration_days=listing.marketing_duration_days(),
    )


@app.get("/listings/{listing_id}/price-history", response_model=list[schemas.PriceHistoryEntryOut])
def get_price_history(listing_id: uuid.UUID, session: Session = Depends(get_session)):
    listing = session.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(404, "Listing nicht gefunden")
    return price_history(listing)


@app.post("/listings/{listing_a_id}/merge/{listing_b_id}")
def merge_listings(
    listing_a_id: uuid.UUID,
    listing_b_id: uuid.UUID,
    target_property_id: uuid.UUID | None = None,
    override_single_feature: bool = False,
    session: Session = Depends(get_session),
):
    listing_a = session.get(Listing, listing_a_id)
    listing_b = session.get(Listing, listing_b_id)
    if listing_a is None or listing_b is None:
        raise HTTPException(404, "Listing nicht gefunden")

    candidate = dedup_engine.score_similarity(listing_a, listing_b)
    target_property = session.get(Property, target_property_id) if target_property_id else None

    try:
        target = dedup_engine.confirm_merge(
            session,
            listing_a=listing_a,
            listing_b=listing_b,
            candidate=candidate,
            performed_by="api-user",
            target_property=target_property,
            override_single_feature=override_single_feature,
        )
    except dedup_engine.MergeNotJustifiedError as exc:
        raise HTTPException(409, str(exc)) from exc
    session.commit()
    return {
        "property_id": str(target.id),
        "combined_score": str(candidate.combined_score),
        "strong_features": candidate.strong_features,
    }


@app.get("/properties/{property_id}", response_model=schemas.PropertyOut)
def get_property(property_id: uuid.UUID, session: Session = Depends(get_session)):
    prop = session.get(Property, property_id)
    if prop is None:
        raise HTTPException(404, "Property nicht gefunden")
    return schemas.PropertyOut(
        id=prop.id,
        property_type=prop.property_type,
        address_raw_text=prop.primary_address.raw_text,
        listing_ids=[l.id for l in prop.listings],
    )


def _run_to_out(run: ValuationRun) -> schemas.ValuationRunOut:
    return schemas.ValuationRunOut(
        id=run.id,
        valuation_date=run.valuation_date,
        value_type=run.value_type,
        as_is_low_eur=(Decimal(run.as_is_low_cents) / 100),
        as_is_base_eur=(Decimal(run.as_is_base_cents) / 100),
        as_is_high_eur=(Decimal(run.as_is_high_cents) / 100),
        central_value_method=run.central_value_method,
        confidence_score=run.confidence_score,
        confidence_breakdown=run.confidence_breakdown,
        warnings=run.warnings or [],
        is_current=run.is_current,
        trigger=run.trigger,
    )


@app.get("/properties/{property_id}/valuation", response_model=schemas.ValuationRunOut)
def get_current_valuation(property_id: uuid.UUID, session: Session = Depends(get_session)):
    run = (
        session.query(ValuationRun)
        .filter_by(property_id=property_id, is_current=True)
        .one_or_none()
    )
    if run is None:
        raise HTTPException(
            404,
            "NOT_RELIABLY_DETERMINABLE: keine aktuelle Bewertung vorhanden "
            "(Regel C.47-C.48 - keine Zahl wird erfunden).",
        )
    return _run_to_out(run)


@app.get("/valuations/{run_id}/discount", response_model=schemas.AsIsDiscountOut)
def get_as_is_discount(run_id: uuid.UUID, asking_price_eur: Decimal, session: Session = Depends(get_session)):
    run = session.get(ValuationRun, run_id)
    if run is None:
        raise HTTPException(404, "ValuationRun nicht gefunden")
    result = as_is_discount(int(asking_price_eur * 100), run)
    return schemas.AsIsDiscountOut(
        as_is_discount_eur=(Decimal(result["as_is_discount_cents"]) / 100),
        as_is_discount_percent=result["as_is_discount_percent"],
        label=result["label"],
        value_type=result["value_type"],
        confidence_score=result["confidence_score"],
    )
