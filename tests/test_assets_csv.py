"""Asset CSV parsing tests."""
from pathlib import Path

from rollover.assets import read_assets, read_assets_from_text


def test_read_assets_basic(tmp_path: Path) -> None:
    csv_text = (
        "asset_id,name,vendor,product,version,seat_count,feature_usage,contract_end_date,annual_spend\n"
        "a1,Laptop fleet,Microsoft,Microsoft 365 E5,2024,50,core,2025-09-01,12000\n"
        "a2,CRM,Salesforce,Salesforce Classic,2023,20,heavy,2025-03-01,5000\n"
    )
    p = tmp_path / "assets.csv"
    p.write_text(csv_text)
    assets = read_assets(p)
    assert len(assets) == 2
    assert assets[0].asset_id == "a1"
    assert assets[0].seat_count == 50


def test_header_order_robust() -> None:
    csv_text = (
        "product,vendor,asset_id\n"
        "Microsoft 365 E5,Microsoft,x1\n"
    )
    assets = read_assets_from_text(csv_text)
    assert len(assets) == 1
    assert assets[0].vendor == "Microsoft"
    assert assets[0].product == "Microsoft 365 E5"


def test_missing_rows_skipped() -> None:
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n\n   \n"
    assets = read_assets_from_text(csv_text)
    assert len(assets) == 1
