# Real Estate Acquisition Intelligence System — Backend

Foundation build for the Berlin/Brandenburg launch market. See
`../docs/ENGINE_STATUS.md` for exactly what is implemented, partially
implemented, or schema-only across all 20 specified engines — read that
before assuming any capability exists.

Stack: Python, SQLAlchemy 2.0, Alembic, FastAPI. PostgreSQL is the
production target; SQLite is used for local dev/tests against the
identical model definitions.

## Setup

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Always use `python -m pip ...` inside the venv rather than a bare `pip`
— on some environments `pip` on `PATH` still resolves to the system
installation even after `source .venv/bin/activate`.

## Run the API

```bash
source .venv/bin/activate
uvicorn app.api.main:app --reload
```

Defaults to a local SQLite file `acquisition_platform.db`. For Postgres:

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/acquisition_platform"
alembic upgrade head
uvicorn app.api.main:app --reload
```

Then seed the Berlin/Brandenburg source registry once:

```bash
curl -X POST http://localhost:8000/admin/seed-sources
```

Open `http://localhost:8000/docs` for interactive API docs, and
`GET /engine-status` for a machine-readable summary of what's real.

## Tests

```bash
source .venv/bin/activate
python -m pytest -q
```

All tests run against an isolated in-memory SQLite database per test
(see `tests/conftest.py`) — they never touch the dev database file.

## Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

Known quirk: Alembic's autogenerate does not always add the
`import app.models.base` line needed for columns using the custom `GUID`/
`JSONVariant` types (see `app/models/base.py`) — check the generated
migration file for `NameError`-shaped issues (bare `app.models.base.GUID()`
without an import) before committing it.

## Layout

- `app/core/` — value objects with no DB dependency: `Money` (cent-accurate),
  `Confidence` scoring, enums shared across engines.
- `app/models/` — SQLAlchemy models. `datapoint.py` is the generic
  append-only fact/provenance ledger everything else can hang off of;
  `stubs.py` holds schema-only tables for engines not yet built (Regel
  C.1/C.17-C.20/Engine 03 provenance rules apply platform-wide, not just
  to the tables that happen to use `DataPoint` directly).
- `app/engines/` — the actual business logic: `source_registry.py`,
  `listing_import.py`, `dedup.py`, `comparable_engine.py`,
  `valuation_engine.py`.
- `app/api/` — a thin FastAPI layer over the engines above. It adds no
  business rules of its own.
- `tests/` — one file per engine plus `test_api.py`, `test_provenance.py`,
  `test_money.py`. Several tests are explicitly written against Teil J
  acceptance tests from the specification (see test docstrings for which).
