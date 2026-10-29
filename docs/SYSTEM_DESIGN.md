# System Design — rollover-auditor

## Problem
Enterprise CIOs with a large IT asset inventory get blindsided when mega-vendors force
tier changes, license-metric swaps, or EOL migrations. rollover-auditor answers: which
assets are exposed, how severe is the exposure, and what contractual/deflection
paths exist — for one specific estate, deterministically and reproducibly.

## Philosophy
- No LLM in the pipeline. Heuristics + templates, versioned in Git. Repro is the point.
- No live scraping of vendor sites. The registry is a curated, git-versioned JSON file.
- Single-tenant in v0.1.0. Enterprise multi-tenancy is explicitly scoped to later issues.

## Components

```
CSV -> assets (ingestion) -> matching (vendor+product join) -> score (heuristic) -> deflection (template) -> report (md/text/pdf)
                                   |                                          |
                                   v                                          v
                           registry (8 curated scenarios)         deflection_strategy templates
                                                                  fastapi app: /health, /registry, /report, /me (JWT-protected)
```

### (1) Ingestion — `src/rollover/assets.py`
- CSV -> list[Asset] using header aliasing (canonical keys with allowed synonyms).
- Forgiving of malformed rows; seat-count defaults to 1, unknown usage tier contributes 0.
- Hyphen/underscore aliases normalized.

### (2) Registry — `src/rollover/registry.py` + `src/rollover/data/vendor_upgrades.json`
- 8 curated scenarios across Microsoft (E5->E7), Salesforce (Classic->Lightning),
  SAP (ECC->S4/HANA), Oracle (Java free->paid), VMware (vSphere->VCF),
  IBM (MQ PVU->VPC), Atlassian (Server->Cloud), Adobe (perpetual->subscription).
- Each has deflection_strategy, typical_cost_formula label (per_seat*12, fixed fee,
  rule-based), impact_estimate, notes. Git-versioned for review.

### (3) Matching — `src/rollover/matching.py`
- `match_upgrades(asset, upgrades)`: normalised vendor + product-token join. No
  vendor-only fallback (avoids "any Microsoft product -> M365 upgrade").
- `score_risk(asset, upgrades, today)`: heuristic 0..100, drained into explicit
  factors. Weights documented in module docstring; not a calibrated probability.

### (4) Deflection — `src/rollover/deflection.py`
  Template-based (never an LLM), per cost posture. Pure-function mapping.

### (5) Reporting — `src/rollover/report.py`
- render_markdown: frozen-form report (bands + exposure table + per deflection +
  registry listing). Deterministic.
- render_text: plain derivation (sanitized pipes).
- render_pdf_bytes: fpdf2 latin-1 safe with line wrap @ 100 cols.

### (6) Auth — `src/rollover/auth/jwt.py` + `auth/dependencies.py`
- PyJWT HS256, secret sourced from `DEVFLOW_JWT_SECRET` (minimum 32 bytes),
  **fail-closed** (no demo-secret fallback).
- bcrypt password hashing (passlib, explicit 72-byte truncation).
- CORS `allow_origins=["*"]`, `allow_credentials=False` (valid).
- Borrowed and hardened from prior `devflow-api` auth work.

### (7) API — `src/rollover/app.py`
- FastAPI factory. `/health`, `/registry`, `/me` (JWT protected), `/report`
  (POST CSV, size-capped 4MB, format=markdown|text|pdf).

## Hard constraints
- No external calls at runtime.
- Single-tenant in v0.1.0.
- Auth secret density enforced at import (module fails to load without it).
- Registry is curated (manual accuracy wins over up-to-table automation).

## Known gaps (filed issues)
- #2 weights are not calibrated; needs citations + config exposure.
- #3 multi-tenant + RBAC + audit logs before enterprise claim.
- #4 PDF rendering is a cell-dump; upgrade to HTML template + optional docx.

## CI
- ruff (gate), mypy --strict, pytest (asyncio auto).
- GitHub Actions, Python 3.11, uv managed.

## Credits
Built as a portfolio evidence repo exercising full PR-team engineering workflow:
PR -> adversarial review + test-augmentation -> CI gate -> merge -> release tag.
