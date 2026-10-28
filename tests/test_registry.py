"""Registry tests."""
from rollover.registry import load_registry


def test_registry_has_at_least_six() -> None:
    upgrades = load_registry()
    assert len(upgrades) >= 6


def test_registry_vendors() -> None:
    upgrades = load_registry()
    vendors = {u.vendor for u in upgrades}
    assert "Microsoft" in vendors
    assert "Salesforce" in vendors
    assert "SAP" in vendors


def test_vendor_upgrade_coerced_date() -> None:
    upgrades = load_registry()
    for u in upgrades:
        assert u.enforced_date is None or u.enforced_date.year >= 2000


def test_deflection_strategies() -> None:
    upgrades = load_registry()
    for u in upgrades:
        assert u.deflection_strategy
        assert u.typical_cost_formula
        assert u.impact_estimate
