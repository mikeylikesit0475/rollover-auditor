"""Domain models for the rollover auditor.

Plain dataclasses so the pipeline stays trivially serialisable and
testable without a database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Asset:
    asset_id: str
    name: str
    vendor: str
    product: str
    version: str
    seat_count: int = 1
    owner: str = ""
    contract_end_date: date | None = None
    feature_usage: str = ""
    annual_spend: float = 0.0
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Contract:
    vendor: str
    product: str
    renewal_date: date | None = None
    account_manager: str = ""
    notes: str = ""


@dataclass(frozen=True)
class VendorUpgrade:
    vendor: str
    product_from: str
    product_to: str
    enforced_date: date | None = None
    deflection_strategy: str = ""
    typical_cost_formula: str = ""
    impact_estimate: str = ""
    notes: str = ""


@dataclass(frozen=True)
class RiskScore:
    asset_id: str
    score: int
    factors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Deflection:
    asset_id: str
    upgrade_vendor: str
    upgrade_to: str
    recommendation: str
