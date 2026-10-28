"""Extended registry tests."""
from pathlib import Path

from rollover.registry import load_registry

_CURATED = Path("src/rollover/data/vendor_upgrades.json")


def test_registry_exact_8_entries() -> None:
    upgrades = load_registry()
    assert len(upgrades) == 8


def test_registry_json_schema_fields() -> None:
    upgrades = load_registry()
    for u in upgrades:
        assert isinstance(u.vendor, str) and u.vendor
        assert isinstance(u.product_from, str) and u.product_from
        assert isinstance(u.deflection_strategy, str) and u.deflection_strategy


def test_registry_default_path_exists() -> None:
    assert _CURATED.exists()


def test_registry_loads_list_shape() -> None:
    import json
    import tempfile

    # load from a temp file with list shape
    data = [
        {
            "vendor": "TestVendor",
            "product_from": "A",
            "product_to": "B",
            "deflection_strategy": "hold",
            "typical_cost_formula": "fixed fee",
            "impact_estimate": "low",
        }
    ]
    fd, p = tempfile.mkstemp(suffix=".json")
    import os
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh)
    ups = load_registry(Path(p))
    assert len(ups) == 1
    assert ups[0].vendor == "TestVendor"
    Path(p).unlink(missing_ok=True)
