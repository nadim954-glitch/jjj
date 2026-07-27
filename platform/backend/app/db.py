"""Engine/session bootstrap. Production target is PostgreSQL (see
alembic/ for migrations); SQLite is used for local dev and tests against
the identical model definitions in app/models/.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base


def make_engine(url: str = "sqlite:///:memory:"):
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine_kwargs = {}
    if url == "sqlite:///:memory:":
        # A plain SQLite ":memory:" DB is per-connection; SQLAlchemy's
        # default SingletonThreadPool only reuses one connection per
        # thread, so a request served from a worker thread (as
        # FastAPI/TestClient do) would otherwise see a blank schema.
        # StaticPool forces every checkout to share the one connection.
        engine_kwargs["poolclass"] = StaticPool
    engine = create_engine(url, connect_args=connect_args, **engine_kwargs)
    if url.startswith("sqlite"):
        from sqlalchemy import event

        @event.listens_for(engine, "connect")
        def _fk_pragma(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def make_session_factory(engine) -> sessionmaker:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def create_all(engine) -> None:
    import app.models  # noqa: F401  ensure every model module is imported

    Base.metadata.create_all(engine)
