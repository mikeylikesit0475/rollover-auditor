"""Report markdown tests."""
from rollover.assets import read_assets_from_text
from rollover.registry import load_registry
from rollover.report import render_markdown, render_pdf_bytes, render_text


def test_markdown_contains_heading() -> None:
    upgrades = load_registry()
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    assets = read_assets_from_text(csv_text)
    md = render_markdown(assets, upgrades)
    assert "# Rollover Audit Report" in md
    assert "Assets: 1" in md


def test_pdf_bytes() -> None:
    upgrades = load_registry()
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    assets = read_assets_from_text(csv_text)
    md = render_markdown(assets, upgrades)
    b = render_pdf_bytes(md)
    assert isinstance(b, (bytes, bytearray))
    assert len(b) > 100
    assert b.startswith(b"%PDF")


def test_text_render() -> None:
    md = "# hi\n| a | b |"
    assert "hi" in render_text(md)
