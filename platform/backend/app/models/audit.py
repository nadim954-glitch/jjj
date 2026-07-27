"""Regel C.18, 02.22, Engine 20: audit trail and model versioning.

AuditLog entries are append-only and are the mechanism behind Regel C.20
("das System muss jederzeit zeigen können, warum sich eine Bewertung
verändert hat") and Regel 02.22 (every merge/un-merge is logged).
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, GUID, JSONVariant, TimestampMixin, UUIDPKMixin, utcnow


class AuditLog(UUIDPKMixin, Base):
    __tablename__ = "audit_log"

    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONVariant, nullable=True)
    performed_by: Mapped[str] = mapped_column(String(200), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class ModelVersion(UUIDPKMixin, TimestampMixin, Base):
    """Engine 20 (Regel 20.17-20.21): every calculation model/engine
    version is stored explicitly; a new version never silently replaces
    the old one, and must be validated before going active."""

    __tablename__ = "model_versions"

    engine_name: Mapped[str] = mapped_column(String(100), nullable=False)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)
    calibration_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    calibration_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    validated_against_history: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
