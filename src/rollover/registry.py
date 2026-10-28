"""Vendor-upgrade registry: curated, hand-verified scenarios.

Loads ``src/rollover/data/vendor_upgrades.json`` and validates it through
pydantic before returning domain dataclasses. No network access.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from .models import VendorUpgrade


class _UpgradeIn(BaseModel):
    vendor: str
    product_from: str
    product_to: str
    enforced_date: date | None = None
    deflection_strategy: str = ""
    typical_cost_formula: str = ""
    impact_estimate: str = ""
    notes: str = ""

    @field_validator("enforced_date", mode="before")
    @classmethod
    def _coerce_date(cls, value: object) -> date | None:
        if value is None or value == "":
            return None
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))


class Registry(BaseModel):
    upgrades: list[_UpgradeIn] = Field(default_factory=list)


_DATA_PATH = Path(__file__).resolve().parent / "data" / "vendor_upgrades.json"


def load_registry(path: Path | None = None) -> list[VendorUpgrade]:
    """Load and validate the curated vendor-upgrade registry."""
    src = path if path is not None else _DATA_PATH
    raw = json.loads(src.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        raw = {"upgrades": raw}
    parsed = Registry.model_validate(raw)
    return [
        VendorUpgrade(
            vendor=u.vendor,
            product_from=u.product_from,
            product_to=u.product_to,
            enforced_date=u.enforced_date,
            deflection_strategy=u.deflection_strategy,
            typical_cost_formula=u.typical_cost_formula,
            impact_estimate=u.impact_estimate,
            notes=u.notes,
        )
        for u in parsed.upgrades
    ]
