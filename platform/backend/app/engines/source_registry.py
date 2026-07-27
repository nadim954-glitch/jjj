"""Engine 03 - Source Registry seed data for the Berlin/Brandenburg launch
market (Teil H).

Regel C.24: the platform must never bypass a portal's or authority's
access restriction. Regel 03.16-03.17: without a confirmed authorization
on file, `direct_access_enabled` stays False and the connector is exposed
as LICENSE_REQUIRED rather than pretending to be live (Teil I: "Täusche
niemals vor, eine externe Quelle sei live angebunden, wenn lediglich
Dummy-Daten vorhanden sind.").

This module only creates Source/SourcePermission rows - it does not talk
to any external network. Actual connectors (WFS clients, PDF parsers,
etc.) are future work tracked in docs/ENGINE_STATUS.md.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.enums import SourceAccessType, SourceQualityClass
from app.models.source import Source, SourcePermission

# Each entry: (name, quality_class, access_type, geographic_scope,
#              content_description, is_official, direct_access_enabled,
#              disabled_reason, license_required, usage_notes)
_REGISTRY: list[dict] = [
    dict(
        name="Gutachterausschuss für Grundstückswerte Berlin (Immobilienpreis-Info)",
        quality_class=SourceQualityClass.OFFICIAL_AGGREGATE,
        access_type=SourceAccessType.LICENSE_REQUIRED,
        geographic_scope="Berlin",
        content_description=(
            "Amtlich ausgewertete Kauffälle, Preisniveaus, Umrechnungskoeffizienten "
            "(Immobilienpreis-Info). Grundlage für AS_IS/ARV-Marktbezug, nicht für "
            "objektindividuelle Werte."
        ),
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Kostenpflichtiger Bezug; kein Nachweis einer Lizenz hinterlegt.",
        license_required=True,
        usage_notes="Regel 03.15: als amtliche Marktquelle vorbereitet, nicht automatisch verbunden.",
    ),
    dict(
        name="AKS Online Berlin (Automatisiertes Kaufpreisauskunftssystem)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.LICENSE_REQUIRED,
        geographic_scope="Berlin",
        content_description="Direkter Zugriff auf Kaufpreissammlung; erfordert Berechtigung.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="AKS_DIRECT_ACCESS=false: keine Berechtigung hinterlegt (Regel 03.16-03.17).",
        license_required=True,
        usage_notes="Manuell erhaltene AKS-Auswertungen bleiben importierbar (Regel 03.18).",
    ),
    dict(
        name="BORIS Berlin (Bodenrichtwertinformationssystem)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Berlin",
        content_description="Amtliche Bodenrichtwerte mit Zone und Stichtag.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Geodienst-Anbindung noch nicht implementiert; manueller Import verfügbar.",
        license_required=False,
        usage_notes="Regel 03.19-03.20: WFS/Geodienst bevorzugen, sobald Connector existiert.",
    ),
    dict(
        name="Geoportal Berlin (FIS-Broker)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Berlin",
        content_description="Amtliche Geodaten: Bebauungspläne, Denkmalschutz, Lärm, Hochwasser.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Geodienst-Anbindung noch nicht implementiert.",
        license_required=False,
        usage_notes="Trägt Location Engine (04) und Planning Engine (11), sobald implementiert.",
    ),
    dict(
        name="Berliner Mietspiegel",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Berlin",
        content_description="Ortsübliche Vergleichsmiete nach Baujahr, Lage, Ausstattung.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Rental Engine (12) noch nicht implementiert.",
        license_required=False,
        usage_notes="Nur innerhalb des gesetzlich vorgesehenen Anwendungsbereichs nutzbar (Regel 03.29-03.30).",
    ),
    dict(
        name="Baulastenauskunft Berlin",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.MANUAL_IMPORT,
        geographic_scope="Berlin",
        content_description="Baulastenverzeichnis-Auskunft je Flurstück, nur auf Antrag.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Kein automatisierter Zugriff verfügbar/zulässig (Regel C.5, C.25).",
        license_required=False,
        usage_notes="Fehlende Auskunft => BAULAST_STATUS_UNKNOWN, niemals NO_BAULAST.",
    ),
    dict(
        name="Bodenbelastungskataster Berlin (BBK)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.MANUAL_IMPORT,
        geographic_scope="Berlin",
        content_description="Verdachtsflächen und Altlasten je Flurstück.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Kein automatisierter Zugriff verfügbar/zulässig (Regel C.6, C.25).",
        license_required=False,
        usage_notes="Fehlende Auskunft => CONTAMINATION_STATUS_UNKNOWN, niemals NO_CONTAMINATION.",
    ),
    dict(
        name="BORIS Brandenburg (Bodenrichtwertinformationssystem)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Brandenburg",
        content_description="Amtliche Bodenrichtwerte Brandenburg mit Zone und Stichtag.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Geodienst-Anbindung noch nicht implementiert.",
        license_required=False,
        usage_notes="Regel 03.21.",
    ),
    dict(
        name="Gutachterausschüsse Brandenburg (Grundstücksmarktberichte)",
        quality_class=SourceQualityClass.OFFICIAL_AGGREGATE,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Brandenburg (regional je Gutachterausschuss)",
        content_description="Aggregierte Marktberichte je Region; keine objektindividuellen Kauffälle.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Regionale Zuordnung anhand Standort noch nicht automatisiert.",
        license_required=False,
        usage_notes="Regel 03.12, Teil H: zuständiger Ausschuss muss aus Standort bestimmt werden.",
    ),
    dict(
        name="Kommunale Bauleitplanung Brandenburg",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.MANUAL_IMPORT,
        geographic_scope="Brandenburg (gemeindespezifisch)",
        content_description="Flächennutzungs- und Bebauungspläne einzelner Gemeinden.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Keine einheitliche API über alle Gemeinden; Planning Engine (11) noch nicht implementiert.",
        license_required=False,
        usage_notes="Teil H.",
    ),
    dict(
        name="ZVG-Portal (Zwangsversteigerungen, bundesweit)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Bundesweit",
        content_description="Amtliche Zwangsversteigerungstermine, Gericht, Aktenzeichen, Verkehrswert.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Foreclosure-Adapter (Engine 01.33-01.37) noch nicht implementiert.",
        license_required=False,
        usage_notes="Gerichtlicher Verkehrswert wird nie automatisch als eigener Marktwert übernommen (Regel 01.35).",
    ),
    dict(
        name="Destatis (Statistisches Bundesamt)",
        quality_class=SourceQualityClass.OFFICIAL_AGGREGATE,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Bundesweit",
        content_description="Baupreisindizes und sonstige amtliche Preisindizes (GENESIS-Online API).",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Index-Fortschreibungs-Connector noch nicht implementiert.",
        license_required=False,
        usage_notes="Regel 03.27-03.28: allgemeiner Index, keine individuelle Handwerkerrechnung.",
    ),
    dict(
        name="Deutsche Bundesbank (Zins-/Finanzierungsmarktdaten)",
        quality_class=SourceQualityClass.OFFICIAL_AGGREGATE,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Bundesweit",
        content_description="Marktreferenzzinssätze für Baufinanzierungen (Statistik-API).",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Finance Engine (13) noch nicht implementiert.",
        license_required=False,
        usage_notes="Regel 03.25-03.26: niemals als individuelles Kreditangebot bezeichnen.",
    ),
    dict(
        name="Gesetze im Internet (Bund) / Landesrecht Berlin & Brandenburg",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Bundesweit / Berlin / Brandenburg",
        content_description="Amtliche Gesetzestexte (GrEStG, BauGB, ImmoWertV, MietrechtsG etc.).",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Automatischer Änderungsabgleich (Regel 03.24) noch nicht implementiert.",
        license_required=False,
        usage_notes="Regel C.40-C.42: jede Rechts-/Steuerparameteränderung muss versioniert werden.",
    ),
    dict(
        name="UBA-Schimmelleitfaden (Umweltbundesamt)",
        quality_class=SourceQualityClass.OFFICIAL_PRIMARY,
        access_type=SourceAccessType.PUBLIC,
        geographic_scope="Bundesweit",
        content_description="Fachliche Referenz für Feuchte-/Schimmelbewertung.",
        is_official=True,
        direct_access_enabled=False,
        disabled_reason="Water Damage Engine (09) noch nicht implementiert.",
        license_required=False,
        usage_notes="Teil H.",
    ),
    dict(
        name="Manuelle Eingabe / Exposé-Import (URL, PDF, Bild, CSV)",
        quality_class=SourceQualityClass.USER_SUPPLIED,
        access_type=SourceAccessType.MANUAL_IMPORT,
        geographic_scope="Bundesweit (aktuell genutzt: Berlin, Brandenburg)",
        content_description="Nutzergeführter Import einzelner Angebote oder CSV-Batches (Engine 01.2).",
        is_official=False,
        direct_access_enabled=True,
        disabled_reason=None,
        license_required=False,
        usage_notes="Bevorzugt gegenüber Scraping, wo keine lizenzierte API existiert (Regel 01.3-01.4).",
    ),
]


def seed_official_sources(session: Session) -> list[Source]:
    """Idempotent: re-running does not duplicate rows, only fills gaps."""
    created: list[Source] = []
    for entry in _REGISTRY:
        existing = session.query(Source).filter_by(name=entry["name"]).one_or_none()
        if existing is not None:
            created.append(existing)
            continue
        source = Source(
            name=entry["name"],
            quality_class=entry["quality_class"],
            access_type=entry["access_type"],
            geographic_scope=entry["geographic_scope"],
            content_description=entry["content_description"],
            is_official=entry["is_official"],
            direct_access_enabled=entry["direct_access_enabled"],
            direct_access_disabled_reason=entry["disabled_reason"],
            health_status="NOT_CONNECTED" if not entry["direct_access_enabled"] else "OK",
        )
        session.add(source)
        session.flush()
        session.add(
            SourcePermission(
                source_id=source.id,
                license_required=entry["license_required"],
                usage_notes=entry["usage_notes"],
                lawful_automated_access_confirmed=False,
            )
        )
        created.append(source)
    session.flush()
    return created
