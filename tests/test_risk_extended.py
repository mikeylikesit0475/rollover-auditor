"""Extended risk scoring tests."""
from datetime import date

from rollover.assets import read_assets_from_text
from rollover.matching import _USAGE_TIER_SCORES, score_risk
from rollover.registry import load_registry
from rollover.report import _risk_band


def test_risk_band_thresholds() -> None:
    assert _risk_band(0) == "LOW"
    assert _risk_band(39) == "LOW"
    assert _risk_band(40) == "MEDIUM"
    assert _risk_band(69) == "MEDIUM"
    assert _risk_band(70) == "HIGH"
    assert _risk_band(100) == "HIGH"


def test_risk_score_bounds_and_monotonic() -> None:
    upgrades = load_registry()
    today = date(2025, 9, 1)
    low_csv = (
        "asset_id,vendor,product,feature_usage,seat_count,contract_end_date\n"
        "low,Acme,Widget,minimal,1,2030-01-01\n"
    )
    high_csv = (
        "asset_id,vendor,product,feature_usage,seat_count,contract_end_date\n"
        "high,Microsoft,Microsoft 365 E5,core,200,2025-09-02\n"
    )
    low_asset = read_assets_from_text(low_csv)[0]
    high_asset = read_assets_from_text(high_csv)[0]
    low_score = score_risk(low_asset, upgrades, today=today).score
    high_score = score_risk(high_asset, upgrades, today=today).score
    assert 0 <= low_score <= 100
    assert 0 <= high_score <= 100
    assert high_score >= low_score


def test_score_missing_asset_id_no_keyerror() -> None:
    from rollover.models import Asset

    upgrades = load_registry()
    asset = Asset(asset_id="", vendor="Microsoft", product="Microsoft 365 E5", name="", version="")
    s = score_risk(asset, upgrades)
    assert s.asset_id == ""
    assert 0 <= s.score <= 100


def test_usage_tier_scores_keys() -> None:
    assert "core" in _USAGE_TIER_SCORES
    assert _USAGE_TIER_SCORES["core"] >= _USAGE_TIER_SCORES["minimal"]


def test_factors_count_nonnegative() -> None:
    upgrades = load_registry()
    csv_text = "asset_id,vendor,product,feature_usage\nf1,Microsoft,Microsoft 365 E5,core\n"
    assets = read_assets_from_text(csv_text)
    s = score_risk(assets[0], upgrades)
    assert len(s.factors) >= 1
