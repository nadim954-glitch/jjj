"""Regel C.5-C.6: an unchecked Baulastenverzeichnis/Bodenbelastungskataster
means UNKNOWN, never a clean bill of health."""
from __future__ import annotations

from app.models.property_ import LandParcel


def test_land_parcel_defaults_to_unknown_not_clean(session, sample_property):
    parcel = LandParcel(property_id=sample_property.id, designation="Gemarkung X, Flur 1, Flurstück 23")
    session.add(parcel)
    session.commit()

    assert parcel.baulast_status == "BAULAST_STATUS_UNKNOWN"
    assert parcel.contamination_status == "CONTAMINATION_STATUS_UNKNOWN"
    assert parcel.baulast_status != "NO_BAULAST"
    assert parcel.contamination_status != "NO_CONTAMINATION"
