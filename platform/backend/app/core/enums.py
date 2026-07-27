"""Shared enums for the acquisition platform.

These enums encode vocabulary that is mandated by the specification
(Teil B and Regel C.2 in particular) and must not be silently widened
or renamed - other engines depend on the exact values.
"""
from __future__ import annotations

import enum


class DataStatus(str, enum.Enum):
    """Regel C.2: every fact must carry one of these statuses.

    Regel C.3: UNKNOWN must never be auto-converted to a neutral/positive
    status. Regel C.4-C.6: absence of a record is UNKNOWN, never a
    negative-risk-free conclusion (e.g. missing Baulasten check is
    BAULAST_STATUS_UNKNOWN, never NO_BAULAST).
    """

    VERIFIED = "VERIFIED"
    DOCUMENTED = "DOCUMENTED"
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    ESTIMATED = "ESTIMATED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class EngineStatus(str, enum.Enum):
    """Regel C.43: every engine run must expose one of these statuses."""

    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class SourceAccessType(str, enum.Enum):
    """Regel 03.12: distinguish public / registration / license / manual."""

    PUBLIC = "PUBLIC"
    REGISTRATION_REQUIRED = "REGISTRATION_REQUIRED"
    LICENSE_REQUIRED = "LICENSE_REQUIRED"
    MANUAL_IMPORT = "MANUAL_IMPORT"


class SourceQualityClass(str, enum.Enum):
    """Regel 03.3-03.4, 03.31: source quality is separate from data confidence."""

    OFFICIAL_PRIMARY = "OFFICIAL_PRIMARY"
    OFFICIAL_AGGREGATE = "OFFICIAL_AGGREGATE"
    TRANSACTION_VERIFIED = "TRANSACTION_VERIFIED"
    COMMERCIAL_LICENSED = "COMMERCIAL_LICENSED"
    COMMERCIAL_PORTAL = "COMMERCIAL_PORTAL"
    USER_SUPPLIED = "USER_SUPPLIED"
    DOCUMENT_INTELLIGENCE = "DOCUMENT_INTELLIGENCE"
    AI_INFERENCE = "AI_INFERENCE"


class ComparableClass(str, enum.Enum):
    """Engine 05, Regel 05.1-05.5 and Teil B: strictly separate classes."""

    SOLD_COMPARABLE = "SOLD_COMPARABLE"
    ASKING_COMPARABLE = "ASKING_COMPARABLE"
    OFFICIAL_AGGREGATE = "OFFICIAL_AGGREGATE"


class ListingKind(str, enum.Enum):
    """Regel 01.7: purchase vs. rental listings must never be conflated."""

    PURCHASE = "PURCHASE"
    RENTAL = "RENTAL"


class PropertyType(str, enum.Enum):
    """Regel 01.8."""

    CONDOMINIUM_UNIT = "CONDOMINIUM_UNIT"
    SINGLE_FAMILY_HOUSE = "SINGLE_FAMILY_HOUSE"
    MULTI_FAMILY_HOUSE = "MULTI_FAMILY_HOUSE"
    LAND_PARCEL = "LAND_PARCEL"
    COMMERCIAL = "COMMERCIAL"
    FORECLOSURE = "FORECLOSURE"
    OTHER = "OTHER"


class TenancyStatus(str, enum.Enum):
    """Regel 01.23."""

    VACANT = "VACANT"
    OWNER_OCCUPIED = "OWNER_OCCUPIED"
    RENTED = "RENTED"
    PARTIALLY_RENTED = "PARTIALLY_RENTED"
    UNKNOWN = "UNKNOWN"


class AreaType(str, enum.Enum):
    """Regel C.34: these must never be mixed."""

    LIVING_AREA = "LIVING_AREA"  # Wohnfläche
    USABLE_AREA = "USABLE_AREA"  # Nutzfläche
    LAND_AREA = "LAND_AREA"  # Grundstücksfläche
    GROSS_FLOOR_AREA = "GROSS_FLOOR_AREA"  # Bruttogrundfläche
    PLOT_RATIO_AREA = "PLOT_RATIO_AREA"  # Geschossfläche


class AreaOrigin(str, enum.Enum):
    """Regel 02.24-02.28: living area needs a traceable origin; verified
    calculations outrank listing claims (Regel 02.26)."""

    LISTING = "LISTING"
    VERIFIED_CALCULATION = "VERIFIED_CALCULATION"
    DECLARATION_OF_DIVISION = "DECLARATION_OF_DIVISION"
    EXPERT_REPORT = "EXPERT_REPORT"
    FLOORPLAN_ESTIMATE = "FLOORPLAN_ESTIMATE"
    USER_INPUT = "USER_INPUT"


# Regel 02.26-02.27: priority order for resolving conflicting area claims.
# Lower index = higher priority. FLOORPLAN_ESTIMATE is explicitly an estimate
# (Regel 02.28) so it ranks below anything documented.
AREA_ORIGIN_PRIORITY: dict[AreaOrigin, int] = {
    AreaOrigin.EXPERT_REPORT: 0,
    AreaOrigin.DECLARATION_OF_DIVISION: 1,
    AreaOrigin.VERIFIED_CALCULATION: 2,
    AreaOrigin.USER_INPUT: 3,
    AreaOrigin.FLOORPLAN_ESTIMATE: 4,
    AreaOrigin.LISTING: 5,
}


class LocationPrecision(str, enum.Enum):
    """Regel 01.38-01.40: never invent an address; degrade precision instead."""

    EXACT_ADDRESS = "EXACT_ADDRESS"
    STREET_LEVEL = "STREET_LEVEL"
    BLOCK_LEVEL = "BLOCK_LEVEL"
    DISTRICT_LEVEL = "DISTRICT_LEVEL"
    UNKNOWN = "UNKNOWN"


class DealStatus(str, enum.Enum):
    """Teil F: deal status vocabulary. MAKE_OFFER may never be produced by
    score alone (Regel 14.47, Teil F final sentence) - that gate lives in
    the (not yet implemented) Risk & Deal engines, not here."""

    NEW = "NEW"
    WATCH = "WATCH"
    INVESTIGATE = "INVESTIGATE"
    HIGH_PRIORITY = "HIGH_PRIORITY"
    DUE_DILIGENCE = "DUE_DILIGENCE"
    NEGOTIATE = "NEGOTIATE"
    MAKE_OFFER = "MAKE_OFFER"
    REJECT = "REJECT"
