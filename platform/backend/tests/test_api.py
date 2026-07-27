"""Smoke tests for the thin HTTP layer over the implemented engines."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.api.deps import get_session
from app.api.main import app


def _client_with_session(session):
    def _override():
        yield session

    app.dependency_overrides[get_session] = _override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_seed_sources_and_list(session):
    gen = _client_with_session(session)
    client = next(gen)

    resp = client.post("/admin/seed-sources")
    assert resp.status_code == 200
    assert len(resp.json()) > 10

    resp2 = client.get("/sources")
    assert resp2.status_code == 200
    names = [s["name"] for s in resp2.json()]
    assert "BORIS Berlin (Bodenrichtwertinformationssystem)" in names


def test_manual_listing_import_and_fetch(session):
    gen = _client_with_session(session)
    client = next(gen)

    resp = client.post(
        "/listings/manual",
        json={
            "external_listing_id": "API-1",
            "asking_price_eur": "250000",
            "living_area_listing_sqm": "70",
            "description_text": "Sanierungsbedürftige Wohnung.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_new_listing"] is True
    listing_id = body["listing_id"]

    resp2 = client.get(f"/listings/{listing_id}")
    assert resp2.status_code == 200
    assert resp2.json()["external_listing_id"] == "API-1"

    resp3 = client.get(f"/listings/{listing_id}/price-history")
    assert resp3.status_code == 200
    assert len(resp3.json()) == 1


def test_valuation_not_found_returns_not_reliably_determinable(session, sample_property):
    gen = _client_with_session(session)
    client = next(gen)

    resp = client.get(f"/properties/{sample_property.id}/valuation")
    assert resp.status_code == 404
    assert "NOT_RELIABLY_DETERMINABLE" in resp.json()["detail"]
