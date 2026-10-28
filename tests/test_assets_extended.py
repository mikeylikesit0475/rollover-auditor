"""Extended asset CSV ingestion tests."""
from pathlib import Path

from rollover.assets import read_assets, read_assets_from_text


def test_header_aliases_override() -> None:
    csv_text = (
        "hostname,manufacturer,software,quantity,assigned_to,renewal_date,"
        "tier,cost,tags\n"
        "h1,Microsoft,Microsoft 365 E5,50,alice,2025-09-01,core,12000,prod;eu\n"
    )
    assets = read_assets_from_text(csv_text)
    assert len(assets) == 1
    a = assets[0]
    assert a.name == "h1"
    assert a.vendor == "Microsoft"
    assert a.product == "Microsoft 365 E5"
    assert a.seat_count == 50
    assert a.owner == "alice"
    assert a.contract_end_date is not None
    assert a.feature_usage == "core"
    assert a.annual_spend == 12000.0
    assert a.tags == ["prod", "eu"]


def test_header_case_insensitive() -> None:
    csv_text = "ASSET_ID,VENDOR,PRODUCT\nA1,Microsoft,Microsoft 365 E5\n"
    assets = read_assets_from_text(csv_text)
    assert len(assets) == 1
    assert assets[0].asset_id == "A1"
    assert assets[0].vendor == "Microsoft"


def test_header_mixed_case_aliases() -> None:
    csv_text = "AssetId,Manufacturer,Application\nx1,Microsoft,Microsoft 365 E5\n"
    assets = read_assets_from_text(csv_text)
    assert len(assets) == 1
    assert assets[0].vendor == "Microsoft"
    assert assets[0].product == "Microsoft 365 E5"


def test_malformed_rows_do_not_raise(tmp_path: Path) -> None:
    csv_text = (
        "asset_id,vendor,product\n"
        "\n"
        "   \n"
        "only_one_column\n"
        "a1,Microsoft,Microsoft 365 E5,extra,columns,ignored\n"
        "a2,Microsoft,Microsoft 365 E5\n"
    )
    assets = read_assets_from_text(csv_text)
    assert len(assets) >= 2
    assert all(a is not None for a in assets)


def test_read_assets_tmp_path_robust(tmp_path: Path) -> None:
    p = tmp_path / "x.csv"
    p.write_text("asset_id,vendor,product\nz1,Acme,Widget\n")
    assets = read_assets(p)
    assert len(assets) == 1
    assert assets[0].asset_id == "z1"
