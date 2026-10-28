# Architecture (one-pager)

Component map:

- `assets.py`: parse IT asset CSV (header-order robust).
- `registry.py`: load + pydantic-validate curated vendor upgrades.
- `matching.py`: match assets→upgrades; risk = feature-usage tier + contract-end recency + upgrade imminence.
- `deflection.py`: deterministic template recommendations (no LLM).
- `report.py`: markdown/text + PDF stub (fpdf2).
- `app.py`/`api.py`: FastAPI factory; /health, /registry, POST /report, protected /me.
- `auth/jwt.py`, `auth/dependencies.py`: fail-closed JWT + bcrypt.

Data flow: Asset CSV -> assets -> matching (vs registry) -> risk scores + deflections -> report (md/text/pdf). All offline, single-tenant, deterministic.

