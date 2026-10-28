"""Deflection tests."""
from rollover.assets import read_assets_from_text
from rollover.deflection import build_deflection, build_deflections
from rollover.registry import load_registry


def test_deflection_for_each_vendor() -> None:
    upgrades = load_registry()
    for u in upgrades:
        csv_text = f"asset_id,vendor,product\na,{u.vendor},{u.product_from}\n"
        assets = read_assets_from_text(csv_text)
        d = build_deflection(assets[0], upgrades)
        assert d is not None, u.vendor
        assert d.asset_id == "a"
        assert d.upgrade_vendor == u.vendor
        assert d.upgrade_to == u.product_to
        assert u.vendor in d.recommendation
        assert u.product_to in d.recommendation


def test_no_deflection_without_match() -> None:
    upgrades = load_registry()
    assets = read_assets_from_text("asset_id,vendor,product\nz,Acme,Widget\n")
    assert build_deflection(assets[0], upgrades) is None
    assert build_deflections(assets, upgrades) == []


def test_build_deflections_multiple() -> None:
    upgrades = load_registry()
    csv_text = (
        "asset_id,vendor,product\n"
        "m1,Microsoft,Microsoft 365 E5\n"
        "s1,Salesforce,Salesforce Classic\n"
    )
    assets = read_assets_from_text(csv_text)
    defs = build_deflections(assets, upgrades)
    assert len(defs) == 2
