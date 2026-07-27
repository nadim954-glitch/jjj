"""Engine 03 - Source, Provenance & Confidence.

Regel 03.1-03.2: every source gets a stable id and a type.
Regel 03.6-03.8: every data point traces retrieved_at / source_date /
valuation_date back to a Source via a SourceRecord.
Regel 03.16-03.17: paid/authorized-only connectors (e.g. AKS direct access)
default to disabled until a real permission is recorded.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SourceAccessType, SourceQualityClass
from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin


class Source(UUIDPKMixin, TimestampMixin, Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    quality_class: Mapped[SourceQualityClass] = mapped_column(
        Enum(SourceQualityClass, name="source_quality_class"), nullable=False
    )
    access_type: Mapped[SourceAccessType] = mapped_column(
        Enum(SourceAccessType, name="source_access_type"), nullable=False
    )
    # Regel 03.9-03.10: geographic reach and content must be described.
    geographic_scope: Mapped[str] = mapped_column(String(200), nullable=False)
    content_description: Mapped[str] = mapped_column(Text, nullable=False)

    is_official: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Regel 03.16-03.17: connector-level kill switch, defaults closed.
    direct_access_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    direct_access_disabled_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Regel 03.49: health status per external source.
    health_status: Mapped[str] = mapped_column(String(30), default="UNKNOWN", nullable=False)
    last_successful_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    license_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    permissions: Mapped[list["SourcePermission"]] = relationship(back_populates="source")
    records: Mapped[list["SourceRecord"]] = relationship(back_populates="source")


class SourcePermission(UUIDPKMixin, TimestampMixin, Base):
    """Regel C.23-C.25, 03.11-03.14: usage license/access must be checked
    and recorded before a source is treated as usable."""

    __tablename__ = "source_permissions"

    source_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("sources.id"), nullable=False)
    license_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    usage_notes: Mapped[str] = mapped_column(Text, nullable=False)
    verified_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    verified_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Regel C.24: platform must never bypass a portal's/authority's access
    # restriction. This flag records that the check was made.
    lawful_automated_access_confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    source: Mapped[Source] = relationship(back_populates="permissions")


class SourceRecord(UUIDPKMixin, TimestampMixin, Base):
    """One concrete retrieval/import event from a Source. This is what
    DataPoint rows reference so every fact can be traced back to *what was
    actually fetched, when* (Regel 03.6-03.8, 03.40-03.42)."""

    __tablename__ = "source_records"

    source_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("sources.id"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(300), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Regel 03.8, 03.22: stichtag (valuation/reference date) is distinct
    # from the moment we happened to fetch it.
    source_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    valuation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    import_method: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. MANUAL, CSV, API, SCRAPE

    source: Mapped[Source] = relationship(back_populates="records")
