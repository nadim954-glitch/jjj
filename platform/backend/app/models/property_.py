"""Engine 02 - Property Identity & Normalization.

Regel 02.1-02.2: `Listing` (app/models/listing.py) and `Property` are
distinct entities; several Listings can point at one Property.
Regel 02.3, 02.12-02.14: a Property can have several Units and several
LandParcels; a Building can sit on more than one LandParcel.
Regel 02.24-02.28: verified living area outranks a listing's claim -
`AreaOrigin`/`AREA_ORIGIN_PRIORITY` in app/core/enums.py encode that
priority; conflicts are resolved by the dedup engine, never silently.
"""
from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, Numeric, String, Table, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import AreaOrigin, DataStatus, LocationPrecision, PropertyType
from app.models.base import Base, GUID, TimestampMixin, UUIDPKMixin


class Address(UUIDPKMixin, TimestampMixin, Base):
    """Regel 02.4-02.5: decomposed fields plus the untouched original text."""

    __tablename__ = "addresses"

    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    country: Mapped[str] = mapped_column(String(2), default="DE", nullable=False)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Bundesland
    municipality: Mapped[str | None] = mapped_column(String(150), nullable=True)  # Gemeinde
    district: Mapped[str | None] = mapped_column(String(150), nullable=True)  # Ortsteil
    street: Mapped[str | None] = mapped_column(String(200), nullable=True)
    normalized_street: Mapped[str | None] = mapped_column(String(200), nullable=True)  # Regel 02.15
    house_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    house_number_suffix: Mapped[str | None] = mapped_column(String(10), nullable=True)  # Regel 02.16
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Regel 01.38-01.40: if the exact address isn't published, we degrade
    # precision instead of inventing one.
    precision: Mapped[LocationPrecision] = mapped_column(
        Enum(LocationPrecision, name="location_precision"), default=LocationPrecision.EXACT_ADDRESS, nullable=False
    )


class GeoLocation(UUIDPKMixin, TimestampMixin, Base):
    """Polymorphic like DataPoint: attaches to whichever entity needs
    coordinates (Property, Building, LandParcel) so building and parcel
    coordinates can differ (Regel 02.42)."""

    __tablename__ = "geo_locations"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)

    latitude: Mapped[object | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[object | None] = mapped_column(Numeric(9, 6), nullable=True)
    precision: Mapped[LocationPrecision] = mapped_column(
        Enum(LocationPrecision, name="geo_precision"), nullable=False
    )
    source_record_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("source_records.id"), nullable=True)
    captured_at: Mapped[date | None] = mapped_column(Date, nullable=True)


building_land_parcels = Table(
    "building_land_parcels",
    Base.metadata,
    Column("building_id", GUID(), ForeignKey("buildings.id"), primary_key=True),
    Column("land_parcel_id", GUID(), ForeignKey("land_parcels.id"), primary_key=True),
)


class Property(UUIDPKMixin, TimestampMixin, Base):
    """The real-world asset. Distinct from Listing (an offer to sell it)."""

    __tablename__ = "properties"

    primary_address_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("addresses.id"), nullable=False)
    property_type: Mapped[PropertyType] = mapped_column(Enum(PropertyType, name="property_type"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    primary_address: Mapped[Address] = relationship()
    buildings: Mapped[list["Building"]] = relationship(back_populates="property")
    units: Mapped[list["Unit"]] = relationship(back_populates="property")
    land_parcels: Mapped[list["LandParcel"]] = relationship(back_populates="property")
    ownership_structures: Mapped[list["OwnershipStructure"]] = relationship(back_populates="property")
    listings: Mapped[list["Listing"]] = relationship(back_populates="property")  # noqa: F821


class Building(UUIDPKMixin, TimestampMixin, Base):
    """Regel 02.7-02.9: a Building is distinct from a Unit; year_built is
    never conflated with a later modernization year."""

    __tablename__ = "buildings"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)

    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_built_status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus, name="year_built_status"), default=DataStatus.UNKNOWN, nullable=False
    )
    year_built_source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("source_records.id"), nullable=True
    )
    modernization_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    floor_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    has_elevator: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    is_monument_protected: Mapped[bool | None] = mapped_column(Boolean, nullable=True)  # Regel 04.21, UNKNOWN if null

    property: Mapped[Property] = relationship(back_populates="buildings")
    units: Mapped[list["Unit"]] = relationship(back_populates="building")
    land_parcels: Mapped[list["LandParcel"]] = relationship(
        secondary=building_land_parcels, back_populates="buildings"
    )


class LandParcel(UUIDPKMixin, TimestampMixin, Base):
    """Flurstück - Regel 02.12-02.14, 11.1-11.3: own entity, official area
    outranks listing claims."""

    __tablename__ = "land_parcels"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)

    designation: Mapped[str | None] = mapped_column(String(200), nullable=True)  # Gemarkung/Flur/Flurstücksnummer

    area_sqm: Mapped[object | None] = mapped_column(Numeric(12, 2), nullable=True)
    area_status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus, name="land_area_status"), default=DataStatus.UNKNOWN, nullable=False
    )
    area_source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("source_records.id"), nullable=True
    )

    land_use_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Regel C.5-C.6: absence must read as UNKNOWN, never as a clean bill of health.
    baulast_status: Mapped[str] = mapped_column(String(40), default="BAULAST_STATUS_UNKNOWN", nullable=False)
    contamination_status: Mapped[str] = mapped_column(
        String(40), default="CONTAMINATION_STATUS_UNKNOWN", nullable=False
    )

    property: Mapped[Property] = relationship(back_populates="land_parcels")
    buildings: Mapped[list[Building]] = relationship(secondary=building_land_parcels, back_populates="land_parcels")


class OwnershipStructure(UUIDPKMixin, TimestampMixin, Base):
    """Regel 02.39: Erbbaurecht (ground lease) is its own legal object
    type, never conflated with full ownership or WEG condominium."""

    __tablename__ = "ownership_structures"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    legal_type: Mapped[str] = mapped_column(String(40), nullable=False)  # FULL_OWNERSHIP | CONDOMINIUM_WEG | GROUND_LEASE | OTHER
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    property: Mapped[Property] = relationship(back_populates="ownership_structures")


class Unit(UUIDPKMixin, TimestampMixin, Base):
    """A Wohnungseigentum unit or the sole usable space of a house.

    Regel 02.24-02.29: living area is tracked with an explicit origin and
    status so verified figures can outrank listing claims; Regel 02.29
    keeps usable area from silently entering a €/living-m² calculation.
    """

    __tablename__ = "units"

    property_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=False)
    building_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("buildings.id"), nullable=True)

    position_in_building: Mapped[str | None] = mapped_column(String(30), nullable=True)  # VORDERHAUS|HINTERHAUS|SEITENFLUEGEL
    height_position: Mapped[str | None] = mapped_column(String(30), nullable=True)  # DACHGESCHOSS|ERDGESCHOSS|SOUTERRAIN|HOCHPARTERRE|NORMAL
    floor: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rooms: Mapped[object | None] = mapped_column(Numeric(4, 1), nullable=True)
    bathrooms: Mapped[object | None] = mapped_column(Numeric(3, 1), nullable=True)

    living_area_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)
    living_area_origin: Mapped[AreaOrigin | None] = mapped_column(Enum(AreaOrigin, name="living_area_origin"), nullable=True)
    living_area_status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus, name="living_area_status"), default=DataStatus.UNKNOWN, nullable=False
    )
    living_area_source_record_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("source_records.id"), nullable=True
    )
    # Regel 01.18/02.24: the listing's own claim, kept separately and
    # never overwritten even once a verified figure exists (Regel C.35).
    living_area_listing_claim_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)

    usable_area_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)

    miteigentumsanteil: Mapped[str | None] = mapped_column(String(30), nullable=True)  # e.g. "45.32/1000"

    has_elevator_access: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_balcony: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_terrace: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_cellar: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_garden: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_parking: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    ownership_structure_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("ownership_structures.id"), nullable=True
    )

    property: Mapped[Property] = relationship(back_populates="units")
    building: Mapped[Building | None] = relationship(back_populates="units")

    def area_conflict(self) -> bool:
        """Regel C.37: hard warning trigger when listing claim and
        verified area disagree materially."""
        if self.living_area_sqm is None or self.living_area_listing_claim_sqm is None:
            return False
        verified = float(self.living_area_sqm)
        claimed = float(self.living_area_listing_claim_sqm)
        if verified == 0:
            return claimed != 0
        return abs(verified - claimed) / verified > 0.03
