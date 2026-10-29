"""Extended matching tests."""
from rollover.assets import read_assets_from_text
from rollover.deflection import build_deflections
from rollover.matching import match_upgrades
from rollover.registry import load_registry


def test_empty_registry_no_matches() -> None:
    assets = read_assets_from_text("asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n")
    assert match_upgrades(assets[0], []) == []


def test_unknown_vendor_no_match() -> None:
    upgrades = load_registry()
    assets = read_assets_from_text("asset_id,vendor,product\nz1,Acme,Widget\n")
    assert match_upgrades(assets[0], upgrades) == []


def test_empty_asset_list_no_matches() -> None:
    assets = read_assets_from_text("")
    upgrades = load_registry()
    assert assets == []
    assert build_deflections(assets, upgrades) == []


def test_empty_asset_list_direct() -> None:
    assert build_deflections([], load_registry()) == []
