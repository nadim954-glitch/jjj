# Engine Status

This tracks, per Engine (Teil I build order), what is real and tested
versus what is schema-only or missing. Per Teil K ("Definition of Done"),
nothing here is allowed to claim more than it does — if an engine reads
`STUB_SCHEMA_ONLY`, no code path in the app should present its output as
a computed, validated result.

Legend:
- **IMPLEMENTED** — real logic, covered by tests, matches the cited Regeln.
- **PARTIAL** — real logic for a subset of the Regeln; gaps are listed.
- **STUB_SCHEMA_ONLY** — relational tables exist (see `app/models/stubs.py`)
  so other engines can already reference the entity, but no engine logic
  reads or writes them yet.
- **NOT_STARTED** — nothing built.

| # | Engine | Status | Notes |
|---|--------|--------|-------|
| 03 | Source, Provenance & Confidence | **PARTIAL** | `Source`/`SourcePermission`/`SourceRecord` models, Berlin/Brandenburg registry seed (`app/engines/source_registry.py`) per Teil H, generic append-only `DataPoint` provenance ledger (`app/models/datapoint.py`, `app/core/provenance_service.py`), rule-based `Confidence` scoring (`app/core/confidence.py`). Missing: live connectors (WFS/API clients), automatic health checks, automatic legal-parameter change detection (Regel 03.24). |
| 01 | Listing Acquisition | **PARTIAL** | Manual entry + CSV import (`app/engines/listing_import.py`), snapshot-based price/area history, marketing duration, renovation/damage keyword screening (explicitly a screening flag, not a diagnosis), simple text-vs-structured-field conflict detection. Missing: PDF/image exposé import, portal API/scraping adapters (deliberately not built — Regel C.24/Teil I: no adapter may pretend to be live without a lawful, confirmed connection), foreclosure (ZVG) adapter beyond the `ForeclosureDetails` table shape. |
| 02 | Property Identity & Normalization | **PARTIAL** | `Property`/`Building`/`Unit`/`LandParcel`/`OwnershipStructure`/`Address`/`GeoLocation` models with area-type separation (Regel C.34) and area-origin priority (Regel 02.24-02.28); dedup/merge scoring + confirm/unmerge workflow with audit logging (`app/engines/dedup.py`) enforcing "no single feature merges automatically" (Regel 02.18). Missing: geocoding connector, image-based similarity signal, historical-address handling (Regel 02.43). |
| 04 | Location & Geospatial Intelligence | **NOT_STARTED** | `GeoLocation` table exists (polymorphic, entity_type/entity_id) but no distance/ÖPNV/noise/flood/Bodenrichtwert-zone logic. |
| 05 | Comparable & Market Data | **IMPLEMENTED (core subset)** | `Comparable`/`ComparableSet`/`MarketDataPoint` models; `app/engines/comparable_engine.py`: strict class separation (SOLD/ASKING/OFFICIAL_AGGREGATE), per-dimension similarity breakdown (distance/time/size/condition/year/features, each a labeled product parameter), IQR-based outlier flagging (never deletes), median/weighted-median/quartiles, radius/time-window expansion logging, minimum-sample confidence warning. Missing: automatic radius/time expansion driver (currently a manual call), Bodenrichtwert-zone boundary handling (Regel 04.37-04.38). |
| 06 | Valuation | **IMPLEMENTED (core subset)** | `ValuationRun`/`ValuationMethodResult` models, append-only versioning (a new run never overwrites the previous one); `app/engines/valuation_engine.py`: AS_IS_LOW/BASE/HIGH range that widens as confidence drops, MARKET_VALUE vs. INDICATIVE_VALUE gate, refuses to fabricate a value when comparable data is insufficient (raises `InsufficientDataForValuation`), Teil E's `AS_IS_DISCOUNT_EUR`/`AS_IS_DISCOUNT_PERCENT` with the MARKET_UNDERVALUE/INDICATIVE_DISCOUNT distinction. Missing: income/Sachwert methods, ARV (post-renovation) valuation, double-counting check across methods (Regel 06.43-06.44), method-disagreement review trigger (Regel 06.36). |
| 07 | Property Condition | **STUB_SCHEMA_ONLY** | `ConditionAssessment`, `ComponentCondition`. |
| 08 | Renovation & Construction Cost | **STUB_SCHEMA_ONLY** | `RenovationScenario`, `RenovationItem`, `CostLibraryItem`. |
| 09 | Water Damage, Moisture & Mold | **STUB_SCHEMA_ONLY** | `DamageCase`, `MoistureMeasurement`, `WaterDamageAssessment`. |
| 10 | WEG Intelligence | **STUB_SCHEMA_ONLY** | `WEG`, `WEGDocument`, `WEGMeasure`, `WEGFinancialStatus`. |
| 11 | Land, Planning & Development | **STUB_SCHEMA_ONLY** | `PlanningAssessment`, `PlanningRule`, `LandAssessment`. `LandParcel.baulast_status`/`contamination_status` default to the `..._STATUS_UNKNOWN` sentinels required by Regel C.5-C.6. |
| 12 | Rental & Tenancy | **STUB_SCHEMA_ONLY** | `RentalAssessment`, `Lease`. |
| 13 | Financing & Acquisition Cost | **STUB_SCHEMA_ONLY** | `FinanceScenario`. |
| 14 | Deal Economics, Strategy & MAO | **STUB_SCHEMA_ONLY** | `InvestmentPolicy`, `InvestmentScenario`, `DealAnalysis`. `DealAnalysis.deal_status` defaults to `NEW` and is never set to `MAKE_OFFER` by any code path yet — that requires Engine 15's Risk Gate Check, which does not exist yet either. |
| 15 | Risk & Due Diligence | **STUB_SCHEMA_ONLY** | `RiskItem`, `DueDiligenceItem`. |
| 16 | Document Intelligence | **STUB_SCHEMA_ONLY** | `Document`, `DocumentExtraction`. |
| 17 | Photo & Visual Intelligence | **STUB_SCHEMA_ONLY** | `Image`, `ImageFinding`. |
| 18 | Search, Opportunity Detection & Ranking | **NOT_STARTED** | Depends on Engine 14/15 existing first. |
| 19 | UI, Deal Room & Workflow | **NOT_STARTED** | No frontend yet; see "What a real next phase looks like" below. |
| 20 | Learning, Calibration, Validation & QA | **PARTIAL** | `ModelVersion`/`ActualProjectResult` models exist. Automated validator (Regel 20.41-20.49) and prognosis-vs-reality error analysis: not built. Tests in `backend/tests/` cover a subset of the Teil J acceptance tests (see below) as a first slice of Engine 20's "automated tests per engine" requirement. |

## Why this order and this cut line

Teil I's build order is: data architecture → source registry/provenance →
property/listing models → import/dedup → geocoding → comparable engine →
valuation engine → condition → renovation → water damage → WEG →
land/planning → rental → finance → deal → risk/DD → search/ranking →
dashboard → learning. This build stops after Valuation (with geocoding
left as a named gap, since it requires a live geocoding connector this
environment has no authorized/licensed access to) because that is the
first point where the specification's central question — "what is this
object actually worth today, traceably, with visible uncertainty" — can
be answered end-to-end with real logic instead of a placeholder. Every
Regel in Teil C (global rules: status vocabulary, no fabrication, no
double counting, append-only versioning, German money formatting, etc.)
that applies to the built engines is implemented, not just described.

## What a real next phase looks like

In order, each needing the previous: Condition Engine (07) → Renovation
Engine (08, consumes Condition output) → Water Damage Engine (09, a
specialization that needs 07/08 plumbing) → WEG Engine (10) → Land/
Planning Engine (11) → Rental Engine (12) → Finance Engine (13, consumes
08+11+12 outputs) → Deal Engine (14, the MAO/ALL_IN_COST math needs 08+11+
12+13) → Risk & Due Diligence (15, the Risk Gate Check that alone may
block MAKE_OFFER) → Search/Ranking (18) → the actual UI (19) → Learning/
Calibration (20, needs real outcomes to have accumulated first). None of
these should be built as a "shape only" pass across all of them at once —
each one, once started, should be built the way 05/06 were: real
computation, tests against the relevant Teil J acceptance tests, and an
honest status update here.

## Feature flags

Connector-level flags live on `Source.direct_access_enabled` (see
`app/engines/source_registry.py`) rather than in a separate config file,
since Regel 03.16-03.17 ties them to a specific, auditable source record
(`SourcePermission.lawful_automated_access_confirmed`). All seeded sources
default to `direct_access_enabled=False` — turning one on requires an
actual recorded authorization, never a code change alone.
