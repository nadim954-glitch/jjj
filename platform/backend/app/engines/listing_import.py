"""Engine 01 - Listing Acquisition (manual + CSV import subset).

Implements Regel 01.2 (manual/CSV import), 01.9-01.14 (snapshot-based
history, price-change metrics), 01.19 (commission kept separate and never
defaulted to 0 when unclear - Regel 13.8), 01.29-01.32 (keyword screening
for renovation/damage mentions, explicitly NOT a diagnosis), and
01.41-01.44 (conflicts between free text and structured fields).

Official/licensed APIs are preferred over scraping (Regel 01.3-01.4); this
module intentionally implements only the lawful, always-available path
(manual entry and CSV) so the system never pretends to have a live portal
connector it doesn't actually have (Teil I).
"""
from __future__ import annotations

import csv
import io
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.enums import DataStatus, ListingKind, PropertyType, TenancyStatus
from app.models.listing import Listing, ListingSnapshot
from app.models.source import Source, SourceRecord

RENOVATION_KEYWORDS = [
    "sanierungsbedürftig",
    "renovierungsbedürftig",
    "modernisierungsbedürftig",
    "handwerkerobjekt",
    "sanierungsobjekt",
    "entkernt",
    "entkernung",
    "renovierungsstau",
    "sanierungsstau",
]

DAMAGE_KEYWORDS = [
    "wasserschaden",
    "wasserschäden",
    "feuchtigkeit",
    "feuchteschaden",
    "durchfeuchtet",
    "schimmel",
    "nässe",
]

_AREA_TEXT_RE = re.compile(r"(\d{2,4}(?:[.,]\d+)?)\s*m(?:²|2)\b", re.IGNORECASE)
_YEAR_TEXT_RE = re.compile(r"baujahr\D{0,5}(1[89]\d{2}|20[0-4]\d)", re.IGNORECASE)


@dataclass
class ListingInputRow:
    external_listing_id: str | None
    listing_kind: ListingKind
    property_type: PropertyType
    title: str | None = None
    url: str | None = None
    raw_address_text: str | None = None
    asking_price_eur: Decimal | None = None
    asking_price_status: DataStatus = DataStatus.DOCUMENTED
    commission_eur: Decimal | None = None
    commission_status: DataStatus = DataStatus.UNKNOWN
    commission_notes: str | None = None
    living_area_listing_sqm: Decimal | None = None
    land_area_listing_sqm: Decimal | None = None
    rooms_claimed: Decimal | None = None
    year_built_claimed: int | None = None
    tenancy_status_claimed: TenancyStatus = TenancyStatus.UNKNOWN
    description_text: str | None = None
    raw_fields: dict = field(default_factory=dict)


@dataclass
class ImportResult:
    listing: Listing
    snapshot: ListingSnapshot
    warnings: list[str]
    conflicts: list[dict]
    is_new_listing: bool


def _detect_keywords(text: str | None, vocabulary: list[str]) -> list[str]:
    if not text:
        return []
    lowered = text.lower()
    return [kw for kw in vocabulary if kw in lowered]


def _detect_text_vs_field_conflicts(row: ListingInputRow) -> list[dict]:
    """Regel 01.41-01.44: description text vs. structured fields.

    This is intentionally a plain regex screen, not NLP - Regel 01.32
    applies equally here: it produces a review flag, never a diagnosis.
    """
    conflicts: list[dict] = []
    text = row.description_text or ""

    area_matches = [Decimal(m.replace(",", ".")) for m in _AREA_TEXT_RE.findall(text)]
    if row.living_area_listing_sqm is not None and area_matches:
        if not any(abs(a - row.living_area_listing_sqm) <= Decimal("1.0") for a in area_matches):
            conflicts.append(
                {
                    "field": "living_area_listing_sqm",
                    "structured_value": str(row.living_area_listing_sqm),
                    "text_values_found": [str(a) for a in area_matches],
                    "note": "Regel 01.43: abweichende Flächenangabe im Beschreibungstext gefunden.",
                }
            )

    year_matches = [int(y) for y in _YEAR_TEXT_RE.findall(text)]
    if row.year_built_claimed is not None and year_matches:
        if row.year_built_claimed not in year_matches:
            conflicts.append(
                {
                    "field": "year_built_claimed",
                    "structured_value": row.year_built_claimed,
                    "text_values_found": year_matches,
                    "note": "Regel 01.44: abweichendes Baujahr im Beschreibungstext gefunden.",
                }
            )

    return conflicts


def _build_warnings(row: ListingInputRow) -> list[str]:
    warnings: list[str] = []
    if row.asking_price_eur is None:
        warnings.append("Kaufpreis fehlt - Angebot kann nicht wirtschaftlich bewertet werden.")
    if row.commission_status == DataStatus.UNKNOWN:
        warnings.append(
            "Maklercourtage unklar - wird als UNKNOWN geführt, nicht als 0 € angenommen (Regel 13.8)."
        )
    if row.living_area_listing_sqm is None:
        warnings.append("Wohnfläche (Inserat) fehlt.")
    if row.tenancy_status_claimed == TenancyStatus.UNKNOWN:
        warnings.append("Vermietungsstatus unklar.")
    return warnings


def import_listing(
    session: Session,
    *,
    source: Source,
    row: ListingInputRow,
    recorded_by: str,
    retrieved_at: datetime | None = None,
    import_method: str = "MANUAL",
) -> ImportResult:
    retrieved_at = retrieved_at or datetime.now(timezone.utc)

    source_record = SourceRecord(
        source_id=source.id,
        external_id=row.external_listing_id,
        retrieved_at=retrieved_at,
        import_method=import_method,
        raw_payload=dict(row.raw_fields),
    )
    session.add(source_record)
    session.flush()

    listing: Listing | None = None
    if row.external_listing_id:
        listing = (
            session.query(Listing)
            .filter_by(source_id=source.id, external_listing_id=row.external_listing_id)
            .one_or_none()
        )

    is_new = listing is None
    if is_new:
        listing = Listing(
            source_id=source.id,
            external_listing_id=row.external_listing_id,
            listing_kind=row.listing_kind,
            property_type=row.property_type,
            title=row.title,
            url=row.url,
            raw_address_text=row.raw_address_text,
            first_seen_at=retrieved_at,
            last_seen_at=retrieved_at,
            is_active=True,
        )
        session.add(listing)
        session.flush()
    else:
        listing.last_seen_at = retrieved_at
        listing.is_active = True

    renovation_hits = _detect_keywords(row.description_text, RENOVATION_KEYWORDS)
    damage_hits = _detect_keywords(row.description_text, DAMAGE_KEYWORDS)
    conflicts = _detect_text_vs_field_conflicts(row)

    snapshot = ListingSnapshot(
        listing_id=listing.id,
        source_record_id=source_record.id,
        captured_at=retrieved_at,
        asking_price_cents=(int(row.asking_price_eur * 100) if row.asking_price_eur is not None else None),
        asking_price_status=row.asking_price_status if row.asking_price_eur is not None else DataStatus.UNKNOWN,
        commission_cents=(int(row.commission_eur * 100) if row.commission_eur is not None else None),
        commission_status=row.commission_status,
        commission_notes=row.commission_notes,
        living_area_listing_sqm=row.living_area_listing_sqm,
        land_area_listing_sqm=row.land_area_listing_sqm,
        rooms_claimed=row.rooms_claimed,
        year_built_claimed=row.year_built_claimed,
        tenancy_status_claimed=row.tenancy_status_claimed,
        description_text=row.description_text,
        renovation_keyword_hits=renovation_hits,
        damage_keyword_hits=damage_hits,
        conflict_flags=conflicts,
        raw_fields=row.raw_fields,
    )
    session.add(snapshot)
    session.flush()

    return ImportResult(
        listing=listing,
        snapshot=snapshot,
        warnings=_build_warnings(row),
        conflicts=conflicts,
        is_new_listing=is_new,
    )


def _naive_utc(value: datetime) -> datetime:
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def price_history(listing: Listing) -> list[dict]:
    """Regel 01.11-01.14: absolute/percentage price change and marketing
    duration, derived read-only from the immutable snapshot history."""
    history = []
    previous_price: int | None = None
    previous_date: datetime | None = None
    # SQLite does not actually persist tzinfo on DateTime(timezone=True)
    # columns - a snapshot instance still held in the session's identity
    # map keeps its original aware datetime, but one reloaded fresh from
    # the DB comes back naive. Normalize to naive-UTC for sorting/diffing
    # so behaviour doesn't depend on which objects happen to be cached.
    for snap in sorted(listing.snapshots, key=lambda s: _naive_utc(s.captured_at)):
        entry = {
            "captured_at": snap.captured_at,
            "asking_price_cents": snap.asking_price_cents,
            "absolute_change_cents": None,
            "percent_change": None,
            "days_since_previous": None,
        }
        if previous_price is not None and snap.asking_price_cents is not None:
            entry["absolute_change_cents"] = snap.asking_price_cents - previous_price
            if previous_price != 0:
                entry["percent_change"] = Decimal(snap.asking_price_cents - previous_price) / Decimal(
                    previous_price
                ) * Decimal(100)
        if previous_date is not None:
            entry["days_since_previous"] = (snap.captured_at.date() - previous_date.date()).days
        if snap.asking_price_cents is not None:
            previous_price = snap.asking_price_cents
        previous_date = snap.captured_at
        history.append(entry)
    return history


def import_csv(
    session: Session,
    *,
    source: Source,
    csv_text: str,
    recorded_by: str,
    listing_kind: ListingKind = ListingKind.PURCHASE,
    retrieved_at: datetime | None = None,
) -> list[ImportResult]:
    """Regel 01.2, 01.49: CSV batch import, concluded with a per-row
    quality report (returned to the caller, e.g. for the UI)."""
    reader = csv.DictReader(io.StringIO(csv_text))
    results: list[ImportResult] = []
    for raw in reader:
        row = ListingInputRow(
            external_listing_id=raw.get("external_listing_id") or None,
            listing_kind=listing_kind,
            property_type=PropertyType(raw["property_type"]) if raw.get("property_type") else PropertyType.OTHER,
            title=raw.get("title") or None,
            url=raw.get("url") or None,
            raw_address_text=raw.get("address") or None,
            asking_price_eur=Decimal(raw["asking_price_eur"]) if raw.get("asking_price_eur") else None,
            living_area_listing_sqm=Decimal(raw["living_area_sqm"]) if raw.get("living_area_sqm") else None,
            land_area_listing_sqm=Decimal(raw["land_area_sqm"]) if raw.get("land_area_sqm") else None,
            rooms_claimed=Decimal(raw["rooms"]) if raw.get("rooms") else None,
            year_built_claimed=int(raw["year_built"]) if raw.get("year_built") else None,
            description_text=raw.get("description") or None,
            raw_fields=dict(raw),
        )
        results.append(
            import_listing(
                session,
                source=source,
                row=row,
                recorded_by=recorded_by,
                retrieved_at=retrieved_at,
                import_method="CSV",
            )
        )
    return results
