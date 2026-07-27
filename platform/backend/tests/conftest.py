from __future__ import annotations

import pytest

from app.core.enums import PropertyType, SourceAccessType, SourceQualityClass
from app.db import create_all, make_engine, make_session_factory
from app.engines.source_registry import seed_official_sources
from app.models.property_ import Address, Property
from app.models.source import Source


@pytest.fixture()
def session():
    engine = make_engine("sqlite:///:memory:")
    create_all(engine)
    Session = make_session_factory(engine)
    s = Session()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture()
def manual_source(session) -> Source:
    seed_official_sources(session)
    session.commit()
    return session.query(Source).filter_by(name="Manuelle Eingabe / Exposé-Import (URL, PDF, Bild, CSV)").one()


@pytest.fixture()
def transaction_source(session) -> Source:
    """A stand-in 'notary/registry' source used only to attach
    SOLD_COMPARABLE test fixtures to a SourceRecord - not part of the
    Teil H registry seed."""
    src = Source(
        name="Testquelle: Notarielle Kaufpreissammlung",
        quality_class=SourceQualityClass.TRANSACTION_VERIFIED,
        access_type=SourceAccessType.LICENSE_REQUIRED,
        geographic_scope="Berlin",
        content_description="Testfixture für belegte Kauffälle.",
        is_official=True,
    )
    session.add(src)
    session.commit()
    return src


@pytest.fixture()
def sample_property(session) -> Property:
    address = Address(raw_text="Musterstraße 1, 10115 Berlin", municipality="Berlin", district="Mitte")
    session.add(address)
    session.flush()
    prop = Property(primary_address_id=address.id, property_type=PropertyType.CONDOMINIUM_UNIT)
    session.add(prop)
    session.commit()
    return prop
