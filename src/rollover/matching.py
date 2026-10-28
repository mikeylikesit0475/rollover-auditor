"""Match assets to vendor upgrades; produce exposure risk scores."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from .models import Asset, RiskScore, VendorUpgrade


def _norm(s: str) -> str:
    return (s or "").strip().lower()


_USAGE_TIER_SCORES: dict[str, int] = {
    "core": 40,
    "heavy": 35,
    "standard": 25,
    "light": 15,
    "minimal": 10,
    "none": 0,
}


def match_upgrades(asset: Asset, upgrades: Iterable[VendorUpgrade]) -> list[VendorUpgrade]:
    """Return upgrades applicable to an asset (vendor + product substring match)."""
    out: list[VendorUpgrade] = []
    av = _norm(asset.vendor)
    ap = _norm(asset.product)
    for u in upgrades:
        if (_norm(u.vendor) in av or av in _norm(u.vendor)) and (
            _norm(u.product_from).split("(")[0].strip().split(" ")[0] in ap
            or ap in _norm(u.product_from)
            or _norm(u.product_from) in ap
        ):
            out.append(u)
    # fallback: vendor-only match if no product match found
    if not out:
        for u in upgrades:
            if _norm(u.vendor) in av or av in _norm(u.vendor):
                out.append(u)
    return out


def score_risk(
    asset: Asset,
    upgrades: Iterable[VendorUpgrade],
    today: date | None = None,
) -> RiskScore:
    today = today or date.today()
    matches = match_upgrades(asset, upgrades)
    factors: list[str] = []
    score = 0
    tier = asset.feature_usage or "standard"
    tier_score = _USAGE_TIER_SCORES.get(tier, 10)
    score += tier_score
    if tier in ("core", "heavy"):
        factors.append(f"high feature usage tier '{tier}' (+{tier_score})")
    # contract end-date recency: closer renewal => higher exposure
    if asset.contract_end_date is not None:
        days = (asset.contract_end_date - today).days
        if days <= 0:
            score += 30
            factors.append("contract already expired (+30)")
        elif days <= 90:
            score += 25
            factors.append(f"contract renews within {days}d (+25)")
        elif days <= 180:
            score += 15
            factors.append(f"contract renews within {days}d (+15)")
        elif days <= 365:
            score += 8
            factors.append(f"contract renews within {days}d (+8)")
        else:
            factors.append(f"contract renewal distant ({days}d)")
    else:
        score += 5
        factors.append("no contract end date recorded (+5)")
    # upgrade imminence
    for u in matches:
        if u.enforced_date is not None:
            d = (u.enforced_date - today).days
            if 0 <= d <= 180:
                score += 20
                factors.append(f"{u.vendor} forced upgrade enforced within {d}d (+20)")
            elif d < 0:
                score += 10
                factors.append(f"{u.vendor} forced upgrade already enforced (+10)")
    if asset.seat_count >= 100:
        score += 10
        factors.append(f"large seat count {asset.seat_count} (+10)")
    if not matches:
        factors.append("no matching vendor upgrade scenario")
    score = max(0, min(100, score))
    return RiskScore(asset_id=asset.asset_id, score=score, factors=factors)
