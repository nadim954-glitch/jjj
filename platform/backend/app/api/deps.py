"""FastAPI dependency wiring. Production target is PostgreSQL via
DATABASE_URL (see docs/ENGINE_STATUS.md / backend/README.md); a local
SQLite file is the zero-config default for `uvicorn app.api.main:app`.
"""
from __future__ import annotations

import os

from sqlalchemy.orm import Session

from app.db import create_all, make_engine, make_session_factory

_DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./acquisition_platform.db")
_engine = make_engine(_DATABASE_URL)
create_all(_engine)
_SessionFactory = make_session_factory(_engine)


def get_session():
    session: Session = _SessionFactory()
    try:
        yield session
    finally:
        session.close()
