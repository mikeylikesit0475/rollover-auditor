"""Risk scoring tests."""
from datetime import date

from rollover.assets import read_assets_from_text
from rollover.matching import score_risk
from rollover.registry import load_registry


def test_risk_high_core() -> None:
    upgrades = load_registry()
    csv_text = (
        "asset_id,vendor,product,feature_usage,seat_count,contract_end_date\n"
        "r1,Microsoft,Microsoft 365 E5,core,200,2025-02-01\n"
    )
    assets = read_assets_from_text(csv_text)
    s = score_risk(assets[0], upgrades, today=date(2025, 1, 1))
    assert s.score >= 60
    assert s.asset_id == "r1"


def test_risk_low_distant() -> None:
    upgrades = load_registry()
    csv_text = (
        "asset_id,vendor,product,feature_usage,seat_count,contract_end_date\n"
        "r2,Oracle,Oracle Java SE (free),minimal,5,2030-01-01\n"
    )
    # product must match oracle java upgrade; vendor fallback helps
    assets = read_assets_from_text(csv_text)
    s = score_risk(assets[0], upgrades, today=date(2025, 1, 1))
    assert 0 <= s.score <= 100


def test_risk_factors_list() -> None:
    upgrades = load_registry()
    csv_text = "asset_id,vendor,product,feature_usage\nr3,Microsoft,Microsoft 365 E5,light\n"
    assets = read_assets_from_text(csv_text)
    s = score_risk(assets[0], upgrades)
    assert isinstance(s.factors, list)
    assert len(s.factors) >= 1
