"""Pydantic request/response models for the HTTP API.

Kept intentionally thin: these mirror the engine dataclasses/ORM models
in app/engines and app/models rather than reinventing validation rules -
the engines (not this layer) enforce the Regeln.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.core.enums import DataStatus, ListingKind, PropertyType, TenancyStatus


class ManualListingIn(BaseModel):
    external_listing_id: str | None = None
    listing_kind: ListingKind = ListingKind.PURCHASE
    property_type: PropertyType = PropertyType.CONDOMINIUM_UNIT
    title: str | None = None
    url: str | None = None
    raw_address_text: str | None = None
    asking_price_eur: Decimal | None = None
    commission_eur: Decimal | None = None
    commission_notes: str | None = None
    living_area_listing_sqm: Decimal | None = None
    land_area_listing_sqm: Decimal | None = None
    rooms_claimed: Decimal | None = None
    year_built_claimed: int | None = None
    tenancy_status_claimed: TenancyStatus = TenancyStatus.UNKNOWN
    description_text: str | None = None


class CsvImportIn(BaseModel):
    csv_text: str
    listing_kind: ListingKind = ListingKind.PURCHASE


class ImportResultOut(BaseModel):
    listing_id: uuid.UUID
    snapshot_id: uuid.UUID
    is_new_listing: bool
    warnings: list[str]
    conflicts: list[dict]


class PriceHistoryEntryOut(BaseModel):
    captured_at: datetime
    asking_price_cents: int | None
    absolute_change_cents: int | None
    percent_change: Decimal | None
    days_since_previous: int | None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_listing_id: str | None
    listing_kind: ListingKind
    property_type: PropertyType
    title: str | None
    url: str | None
    raw_address_text: str | None
    is_active: bool
    first_seen_at: datetime
    last_seen_at: datetime
    property_id: uuid.UUID | None
    marketing_duration_days: int


class PropertyOut(BaseModel):
    id: uuid.UUID
    property_type: PropertyType
    address_raw_text: str
    listing_ids: list[uuid.UUID]


class ValuationRunOut(BaseModel):
    id: uuid.UUID
    valuation_date: date
    value_type: str
    as_is_low_eur: Decimal
    as_is_base_eur: Decimal
    as_is_high_eur: Decimal
    central_value_method: str
    confidence_score: Decimal
    confidence_breakdown: dict
    warnings: list[str]
    is_current: bool
    trigger: str


class AsIsDiscountOut(BaseModel):
    as_is_discount_eur: Decimal
    as_is_discount_percent: Decimal | None
    label: str
    value_type: str
    confidence_score: Decimal


class SourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    quality_class: str
    access_type: str
    geographic_scope: str
    is_official: bool
    direct_access_enabled: bool
    direct_access_disabled_reason: str | None
    health_status: str
