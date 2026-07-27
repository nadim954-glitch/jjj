# Real Estate Acquisition Intelligence System

Ankaufskontrolle für unsanierte/schadenbehaftete Wohnimmobilien,
Mehrfamilienhäuser und Grundstücke in Berlin und Brandenburg — mit einer
Architektur, die für alle deutschen Bundesländer erweiterbar ist.

**Start here:**

- [`docs/ENGINE_STATUS.md`](docs/ENGINE_STATUS.md) — what's implemented
  vs. schema-only, across all 20 specified engines. Read this before
  assuming any capability exists; nothing in this codebase is allowed to
  claim more than `ENGINE_STATUS.md` says it does.
- [`backend/README.md`](backend/README.md) — setup, running the API,
  tests, migrations.

This is a foundation build, not the full specification. It implements the
data architecture, Source/Provenance framework, Property/Listing models
with manual+CSV import, deduplication, and the Comparable + Valuation
engines end-to-end with tests — the first slice where the specification's
central question ("what is this object actually worth today, traceably,
with visible uncertainty") can be answered with real logic rather than a
placeholder. Engines 07–20 (Condition, Renovation, Water Damage, WEG,
Land/Planning, Rental, Finance, Deal/MAO, Risk, Document/Photo
Intelligence, Search/Ranking, UI, Learning) have real database schemas
reserved for them but no engine logic yet — see `ENGINE_STATUS.md` for the
recommended build order to continue.
