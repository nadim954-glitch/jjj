"""Schema stubs for Engines 07-20 (Condition, Renovation, Water Damage, WEG,
Land/Planning, Rental, Finance, Deal, Risk/DueDiligence, Document, Image,
Notification, ActualProjectResult).

IMPORTANT - read before extending: these tables exist so the relational
shape described in Teil D is real and extensible, and so downstream tables
(RiskItem, DueDiligenceItem, ...) can already reference a Property/Unit/
Listing. None of them are populated or read by any engine logic yet.
Every class below carries `IMPLEMENTATION_STATUS = "STUB_SCHEMA_ONLY"` and
is listed in docs/ENGINE_STATUS.md - do not present data written into
these tables as if a corresponding engine computed/validated it (Teil I,
Teil K: "Das Projekt ist nicht fertig, wenn..."). Building out the real
engine for any of these means: (1) replace this stub's columns with the
fully specified model from the relevant Engine section, (2) write the
engine module under app/engines/, (3) write tests, (4) flip this file's
entry off the stub list in ENGINE_STATUS.md.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin


class _StubMixin:
    IMPLEMENTATION_STATUS = "STUB_SCHEMA_ONLY"


# --- Engine 07: Property Condition -----------------------------------------


class ConditionAssessment(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 07 (Regel 07.1-07.50). A run that aggregates per-component
    findings; must never be a single-word condition label (Regel 07.1)."""

    __tablename__ = "condition_assessments"

    unit_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("units.id"), nullable=True)
    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    assessed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    overall_summary: Mapped[str | None] = mapped_column(Text, nullable=True)


class ComponentCondition(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 07. One row per Bauteil (Elektrik, Bad, Dach, ...) with its
    own evidence source and derived action (Regel 07.2-07.44)."""

    __tablename__ = "component_conditions"

    condition_assessment_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("condition_assessments.id"), nullable=False)
    component_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="UNKNOWN")
    evidence_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    derived_action: Mapped[str | None] = mapped_column(String(30), nullable=True)  # KEEP|REPAIR|PARTIAL_RENEWAL|REPLACE|INSPECTION_REQUIRED|UNKNOWN
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


# --- Engine 08: Renovation & Construction Cost ------------------------------


class RenovationScenario(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 08 (Regel 08.1-08.50)."""

    __tablename__ = "renovation_scenarios"

    unit_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("units.id"), nullable=True)
    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    target_standard: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Regel 06.28


class RenovationItem(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 08 (Regel 08.1-08.6, 08.45-08.46): quantity × unit price,
    LOW/EXPECTED/HIGH, each with its own source."""

    __tablename__ = "renovation_items"

    renovation_scenario_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("renovation_scenarios.id"), nullable=False)
    trade: Mapped[str] = mapped_column(String(100), nullable=False)  # Gewerk
    description: Mapped[str] = mapped_column(Text, nullable=False)
    quantity: Mapped[object | None] = mapped_column(Numeric(12, 3), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    unit_price_low_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price_expected_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price_high_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_library_item_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("cost_library_items.id"), nullable=True)


class CostLibraryItem(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 08 (Regel 08.5-08.13): market vs. internal cost profiles,
    kept separate (Regel 08.13, Test J.9)."""

    __tablename__ = "cost_library_items"

    trade: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    profile_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MARKET | INTERNAL
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("source_records.id"), nullable=True)


# --- Engine 09: Water Damage, Moisture & Mold -------------------------------


class DamageCase(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 09 (Regel 09.1-09.50)."""

    __tablename__ = "damage_cases"

    unit_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("units.id"), nullable=True)
    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    cause: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False)
    cause_status: Mapped[str] = mapped_column(String(20), default="UNKNOWN", nullable=False)  # KNOWN|LIKELY|UNKNOWN|ACTIVE_UNRESOLVED
    onset_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_prior_case: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class MoistureMeasurement(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 09 (Regel 09.21-09.26): device/method-specific, never
    compared across incompatible methods without justification."""

    __tablename__ = "moisture_measurements"

    damage_case_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("damage_cases.id"), nullable=False)
    room: Mapped[str | None] = mapped_column(String(100), nullable=True)
    measurement_point: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device: Mapped[str | None] = mapped_column(String(100), nullable=True)
    method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    value: Mapped[object | None] = mapped_column(Numeric(8, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    measured_at: Mapped[date | None] = mapped_column(Date, nullable=True)


class WaterDamageAssessment(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 09 (Regel 09.39-09.47): KNOWN/EXPECTED_HIDDEN/WORST_CASE cost
    scenarios feeding DAMAGE_ARBITRAGE."""

    __tablename__ = "water_damage_assessments"

    damage_case_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("damage_cases.id"), nullable=False)
    known_damage_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_hidden_damage_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    worst_case_damage_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)


# --- Engine 10: WEG Intelligence ---------------------------------------------


class WEG(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 10 (Regel 10.1-10.50)."""

    __tablename__ = "wegs"

    building_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("buildings.id"), nullable=True)
    total_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reserve_fund_total_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_allocation_key_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class WEGDocument(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "weg_documents"

    weg_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("wegs.id"), nullable=False)
    document_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("documents.id"), nullable=True)
    document_kind: Mapped[str | None] = mapped_column(String(60), nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)


class WEGMeasure(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 10 (Regel 10.12-10.16): resolved vs. merely discussed must
    stay distinguishable (Test J.4)."""

    __tablename__ = "weg_measures"

    weg_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("wegs.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    resolution_status: Mapped[str] = mapped_column(String(30), default="DISCUSSED_ONLY", nullable=False)  # RESOLVED|DISCUSSED_ONLY
    estimated_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_share_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)


class WEGFinancialStatus(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "weg_financial_status"

    weg_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("wegs.id"), nullable=False)
    as_of_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_arrears_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    outstanding_loans_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)


# --- Engine 11: Land, Planning & Development ---------------------------------


class PlanningAssessment(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 11 (Regel 11.11-11.34): plan status must never be conflated
    with an approved building permit (Test J.6)."""

    __tablename__ = "planning_assessments"

    land_parcel_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("land_parcels.id"), nullable=False)
    plan_status: Mapped[str] = mapped_column(String(40), default="UNKNOWN", nullable=False)  # QUALIFIED_B_PLAN|DRAFT|SECTION_34|SECTION_35|UNKNOWN
    grz: Mapped[object | None] = mapped_column(Numeric(4, 2), nullable=True)
    gfz: Mapped[object | None] = mapped_column(Numeric(4, 2), nullable=True)
    max_floors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scenario_label: Mapped[str | None] = mapped_column(String(30), nullable=True)  # must be INDICATIVE_NOT_APPROVED for §34 (Regel 11.32-11.33)


class PlanningRule(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "planning_rules"

    planning_assessment_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("planning_assessments.id"), nullable=False)
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    rule_type: Mapped[str | None] = mapped_column(String(60), nullable=True)


class LandAssessment(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 11 (Regel 11.4-11.10, 11.48): residual land value is an
    investment value, never automatically the Verkehrswert (Test J.5)."""

    __tablename__ = "land_assessments"

    land_parcel_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("land_parcels.id"), nullable=False)
    bodenrichtwert_eur_per_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)
    bodenrichtwert_zone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bodenrichtwert_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    residual_land_value_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)


# --- Engine 12: Rental & Tenancy ---------------------------------------------


class RentalAssessment(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 12 (Regel 12.1-12.50): actual lease vs. theoretical upside
    must stay distinguishable (Test J.15)."""

    __tablename__ = "rental_assessments"

    unit_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("units.id"), nullable=False)
    current_net_cold_rent_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mietspiegel_indicative_rent_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asking_market_rent_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)


class Lease(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "leases"

    unit_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("units.id"), nullable=False)
    tenancy_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    net_cold_rent_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rent_mechanism: Mapped[str | None] = mapped_column(String(30), nullable=True)  # FIXED|STAFFELMIETE|INDEXMIETE
    document_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("documents.id"), nullable=True)


# --- Engine 13: Financing & Acquisition Cost --------------------------------


class FinanceScenario(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 13 (Regel 13.1-13.50)."""

    __tablename__ = "finance_scenarios"

    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    equity_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    loan_amount_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    interest_rate_pct: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    amortization_rate_pct: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    fixed_rate_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_market_reference_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # Regel 13.24-13.25


# --- Engine 14: Deal Economics, Strategy & MAO ------------------------------


class InvestmentPolicy(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Teil G. `is_screening_default=True` rows must be labeled
    SCREENING_DEFAULT in the UI, never presented as a general rule."""

    __tablename__ = "investment_policies"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    is_screening_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_purchase_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_all_in_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_data_confidence: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    include_water_damage_objects: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    include_land_development: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class InvestmentScenario(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "investment_scenarios"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    investment_policy_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("investment_policies.id"), nullable=True)
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)


class DealAnalysis(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 14/Teil F. `deal_status` may never be MAKE_OFFER purely from
    a score - that gate belongs to Engine 15's Risk Gate Check, not yet
    implemented, so this stub does not compute or assign deal_status."""

    __tablename__ = "deal_analyses"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    investment_scenario_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("investment_scenarios.id"), nullable=True)
    all_in_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mao_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    deal_status: Mapped[str] = mapped_column(String(30), default="NEW", nullable=False)


# --- Engine 15: Risk & Due Diligence -----------------------------------------


class RiskItem(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 15 (Regel 15.1-15.50): a single confirmed Hard Stop must be
    able to override any score (Test J.18)."""

    __tablename__ = "risk_items"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False)
    is_hard_stop: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DueDiligenceItem(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "due_diligence_items"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    criticality: Mapped[str] = mapped_column(String(20), default="OPTIONAL", nullable=False)  # CRITICAL|IMPORTANT|OPTIONAL
    depends_on_calculation: Mapped[str | None] = mapped_column(String(200), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# --- Engine 16: Document Intelligence -----------------------------------------


class Document(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "documents"

    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    listing_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("listings.id"), nullable=True)
    document_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String(300), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(30), default="NOT_STARTED", nullable=False)


class DocumentExtraction(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "document_extractions"

    document_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("documents.id"), nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extracted_field: Mapped[str | None] = mapped_column(String(150), nullable=True)
    extracted_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    parser_version: Mapped[str | None] = mapped_column(String(50), nullable=True)


# --- Engine 17: Photo & Visual Intelligence -----------------------------------


class Image(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "images"

    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    listing_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("listings.id"), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(Text, nullable=True)
    room_label: Mapped[str | None] = mapped_column(String(60), nullable=True)
    room_label_confidence: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ImageFinding(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 17: a visual finding is a hint fed to the Condition Engine,
    never a standalone diagnosis (Regel 17.34-17.36, Test J.28-J.30)."""

    __tablename__ = "image_findings"

    image_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("images.id"), nullable=False)
    finding_type: Mapped[str] = mapped_column(String(60), nullable=False)
    confidence: Mapped[object | None] = mapped_column(Numeric(6, 4), nullable=True)
    is_suspected_only: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# --- Notification / Engine 20 -------------------------------------------------


class Notification(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "notifications"

    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ActualProjectResult(_StubMixin, UUIDPKMixin, TimestampMixin, Base):
    """Engine 20 (Regel 20.1-20.21): realized outcomes for later
    prognosis-vs-reality calibration."""

    __tablename__ = "actual_project_results"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    actual_purchase_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_acquisition_costs_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_renovation_costs_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_project_duration_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_sale_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_achieved_rent_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
