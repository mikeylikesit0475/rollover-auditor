"""Reporting: deterministic markdown + text report, PDF stub via fpdf2."""
from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from fpdf import FPDF

from .deflection import build_deflections
from .matching import score_risk
from .models import Asset, RiskScore, VendorUpgrade


def _risk_band(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def render_markdown(
    assets: list[Asset],
    upgrades: list[VendorUpgrade],
    scores: Iterable[RiskScore] | None = None,
    today: date | None = None,
) -> str:
    today = today or date.today()
    if scores is None:
        scores = [score_risk(a, upgrades, today) for a in assets]
    scores = list(scores)
    score_by = {s.asset_id: s for s in scores}
    defs = {d.asset_id: d for d in build_deflections(assets, upgrades)}
    lines: list[str] = []
    lines.append("# Rollover Audit Report")
    lines.append("")
    lines.append(
        f"Generated: {today.isoformat()}  |  Assets: {len(assets)}  |  "
        f"Scenarios: {len(upgrades)}"
    )
    lines.append("")
    lines.append("## Summary")
    bands = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for s in scores:
        bands[_risk_band(s.score)] += 1
    lines.append(f"- HIGH: {bands['HIGH']}  MEDIUM: {bands['MEDIUM']}  LOW: {bands['LOW']}")
    lines.append("")
    lines.append("## Asset exposure")
    lines.append("")
    lines.append("| Asset | Vendor | Product | Seats | Risk | Factors |")
    lines.append("|---|---|---|---|---|---|")
    for a in assets:
        s_obj = score_by.get(a.asset_id)
        sc = s_obj.score if s_obj is not None else 0
        factors = ";".join(s_obj.factors) if s_obj is not None else ""
        row = (
            f"| {a.asset_id} | {a.vendor} | {a.product} | {a.seat_count} | "
            f"{sc} ({_risk_band(sc)}) | {factors} |"
        )
        lines.append(row)
    lines.append("")
    lines.append("## Deflections")
    lines.append("")
    for a in assets:
        d = defs.get(a.asset_id)
        if d is None:
            continue
        lines.append(f"### {a.asset_id} - {d.upgrade_vendor} -> {d.upgrade_to}")
        lines.append("")
        lines.append(d.recommendation)
        lines.append("")
    lines.append("## Registry (curated)")
    lines.append("")
    for u in upgrades:
        lines.append(
            f"- **{u.vendor}** {u.product_from} -> {u.product_to} "
            f"(enforced {u.enforced_date or 'TBD'})"
        )
    lines.append("")
    return "\n".join(lines)


def render_text(report_md: str) -> str:
    # Plain-text rendering: strip markdown table pipes lightly.
    out = report_md.replace("|", " ")
    return out


def render_pdf_bytes(report_md: str) -> bytes:
    """Placeholder PDF renderer (full build in PR #2)."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in report_md.splitlines():
        # fpdf core fonts only support latin-1; replace unsupported chars.
        safe = line.encode("latin-1", "replace").decode("latin-1")
        pdf.cell(0, 6, safe, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
