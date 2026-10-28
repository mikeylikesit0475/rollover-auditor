"""Deterministic deflection recommendations (template-based; never an LLM)."""
from __future__ import annotations

from .matching import match_upgrades
from .models import Asset, Deflection, VendorUpgrade

_TEMPLATES: dict[str, str] = {
    "per_seat * 12": (
        "Negotiate a per-seat price lock or downgrade before renewal; cap seat growth; "
        "evaluate competitive alternatives for the forced uplift."
    ),
    "fixed fee": (
        "Freeze scope, run a readiness audit, and phase the migration by module to spread "
        "the fixed-fee cost across two budget cycles."
    ),
    "rule-based": (
        "Apply the contractual change-of-terms clause; document non-acceptance in writing "
        "within the notice window."
    ),
}


def build_deflection(asset: Asset, uploads: list[VendorUpgrade]) -> Deflection | None:
    matches = match_upgrades(asset, uploads)
    if not matches:
        return None
    u = matches[0]
    strategy = u.deflection_strategy or "Hold and negotiate at renewal."
    formula_hint = _TEMPLATES.get(u.typical_cost_formula, "Review cost formula and renegotiate.")
    recommendation = (
        f"Asset '{asset.name}' ({asset.asset_id}) is exposed to {u.vendor} "
        f"{u.product_from} -> {u.product_to} (enforced {u.enforced_date or 'TBD'}). "
        f"Strategy: {strategy} Cost posture: {formula_hint} "
        f"Impact: {u.impact_estimate}"
    )
    return Deflection(
        asset_id=asset.asset_id,
        upgrade_vendor=u.vendor,
        upgrade_to=u.product_to,
        recommendation=recommendation,
    )


def build_deflections(assets: list[Asset], upgrades: list[VendorUpgrade]) -> list[Deflection]:
    out: list[Deflection] = []
    for a in assets:
        d = build_deflection(a, upgrades)
        if d is not None:
            out.append(d)
    return out
