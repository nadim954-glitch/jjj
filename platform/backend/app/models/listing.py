"""Engine 01 - Listing Acquisition.

Regel 02.1: Listing is distinct from Property. A Listing may exist before
it has been matched/merged into a Property (property_id nullable until the
dedup engine, app/engines/dedup.py, links it).

Regel 01.9-01.14: original source id is retained, every change produces a
new ListingSnapshot (never mutate history), and price-change metrics are
derived from consecutive snapshots rather than stored as mutable fields.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import DataStatus, ListingKind, PropertyType, TenancyStatus
from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin


class Listing(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "listings"

    property_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("properties.id"), nullable=True)
    source_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("sources.id"), nullable=False)

    # Regel 01.9: the portal/source's own identifier for this listing.
    external_listing_id: Mapped[str | None] = mapped_column(String(300), nullable=True)

    listing_kind: Mapped[ListingKind] = mapped_column(Enum(ListingKind, name="listing_kind"), nullable=False)
    property_type: Mapped[PropertyType] = mapped_column(Enum(PropertyType, name="listing_property_type"), nullable=False)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Regel 01.38-01.40: whatever the portal actually published, unnormalized.
    # Never fabricate a precise address if this is vague/absent.
    raw_address_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Regel 01.15-01.16: relisting/broker-change detection outcome, not a
    # new object identity by itself.
    relisted_from_listing_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("listings.id"), nullable=True)

    property: Mapped["Property | None"] = relationship(back_populates="listings")  # noqa: F821
    snapshots: Mapped[list["ListingSnapshot"]] = relationship(
        back_populates="listing", order_by="ListingSnapshot.captured_at"
    )
    foreclosure_details: Mapped["ForeclosureDetails | None"] = relationship(back_populates="listing", uselist=False)

    def marketing_duration_days(self) -> int:
        """Regel 01.14."""
        return (self.last_seen_at.date() - self.first_seen_at.date()).days


class ListingSnapshot(UUIDPKMixin, Base):
    """One immutable observation of a listing's mutable fields.

    Regel 01.10-01.13: every listing change is a new snapshot; absolute
    and percentage price changes are computed from consecutive snapshots,
    never stored as an editable field.
    """

    __tablename__ = "listing_snapshots"

    listing_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("listings.id"), nullable=False)
    source_record_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("source_records.id"), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    asking_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    asking_price_status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus, name="asking_price_status"), default=DataStatus.UNKNOWN, nullable=False
    )

    # Regel 01.19, 13.7-13.8: commission is tracked separately and an
    # unclear commission must stay UNKNOWN, never default to 0.
    commission_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    commission_status: Mapped[DataStatus] = mapped_column(
        Enum(DataStatus, name="commission_status"), default=DataStatus.UNKNOWN, nullable=False
    )
    commission_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    living_area_listing_sqm: Mapped[object | None] = mapped_column(Numeric(10, 2), nullable=True)
    land_area_listing_sqm: Mapped[object | None] = mapped_column(Numeric(12, 2), nullable=True)
    rooms_claimed: Mapped[object | None] = mapped_column(Numeric(4, 1), nullable=True)
    year_built_claimed: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tenancy_status_claimed: Mapped[TenancyStatus] = mapped_column(
        Enum(TenancyStatus, name="tenancy_status_claimed"), default=TenancyStatus.UNKNOWN, nullable=False
    )

    description_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Regel 01.29-01.31: keyword-flagged mentions (renovation need, water
    # damage, mold, ...) - a screening flag only, never a diagnosis
    # (Regel 01.32).
    renovation_keyword_hits: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)
    damage_keyword_hits: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)

    # Regel 01.41-01.44: contradictions between free text and structured
    # fields, or between structured fields across snapshots/sources.
    conflict_flags: Mapped[list | None] = mapped_column(JSONVariant, nullable=True)

    raw_fields: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)

    listing: Mapped[Listing] = relationship(back_populates="snapshots")


class ForeclosureDetails(UUIDPKMixin, Base):
    """Regel 01.33-01.37: court, case number, hearing date and the
    published Verkehrswert kept separate from our own valuation."""

    __tablename__ = "foreclosure_details"

    listing_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("listings.id"), nullable=False, unique=True)
    court_name: Mapped[str] = mapped_column(String(200), nullable=False)
    case_reference: Mapped[str] = mapped_column(String(100), nullable=False)
    hearing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    published_verkehrswert_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    appraisal_date: Mapped[date | None] = mapped_column(Date, nullable=True)  # Regel 01.36

    listing: Mapped[Listing] = relationship(back_populates="foreclosure_details")
