"""PDF renderer tests."""
from rollover.report import render_pdf_bytes


def test_pdf_starts_with_magic() -> None:
    b = render_pdf_bytes("# hi")
    assert b.startswith(b"%PDF-")


def test_pdf_unicode_large_no_crash() -> None:
    text = "line\n" * 1000 + "unicode \u00e9 \u4e2d \U0001f600\n"
    b = render_pdf_bytes(text)
    assert b.startswith(b"%PDF-")
    assert len(b) > 0
