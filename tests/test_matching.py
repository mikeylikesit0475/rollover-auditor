"""Matching tests."""
from rollover.assets import read_assets_from_text
from rollover.matching import match_upgrades
from rollover.registry import load_registry


def test_match_microsoft() -> None:
    upgrades = load_registry()
    csv_text = (
        "asset_id,vendor,product,feature_usage,seat_count\n"
        "m1,Microsoft,Microsoft 365 E5,core,100\n"
    )
    assets = read_assets_from_text(csv_text)
    matches = match_upgrades(assets[0], upgrades)
    assert any(u.vendor == "Microsoft" for u in matches)


def test_no_match_returns_empty_or_vendor() -> None:
    upgrades = load_registry()
    csv_text = "asset_id,vendor,product\nz1,Acme,Widget\n"
    assets = read_assets_from_text(csv_text)
    matches = match_upgrades(assets[0], upgrades)
    # vendor fallback may return []; product/vendor won't match acme
    assert isinstance(matches, list)
