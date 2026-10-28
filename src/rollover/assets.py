"""Read an IT asset inventory CSV into ``Asset`` dataclasses.

Robust to header order and missing columns; never raises on malformed rows.
"""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .models import Asset


def _date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _int(value: str) -> int:
    try:
        return int(float(value.strip()))
    except (ValueError, AttributeError):
        return 1


def _float(value: str) -> float:
    try:
        return float(value.strip())
    except (ValueError, AttributeError):
        return 0.0


_HEADER_ALIASES: dict[str, set[str]] = {
    "asset_id": {"asset_id", "assetid", "id", "device_id"},
    "name": {"name", "asset_name", "hostname", "device_name"},
    "vendor": {"vendor", "manufacturer", "supplier"},
    "product": {"product", "software", "application", "title"},
    "version": {"version", "release", "ver"},
    "seat_count": {"seat_count", "seats", "licenses", "quantity", "qty"},
    "owner": {"owner", "assigned_to", "user"},
    "contract_end_date": {
            "contract_end_date", "contract_end", "renewal_date", "end_date", "expiry",
        },
    "feature_usage": {"feature_usage", "feature_tier", "usage", "tier", "usage_tier"},
    "annual_spend": {"annual_spend", "spend", "cost", "annual_cost"},
    "tags": {"tags", "labels", "categories"},
}


def _col(headers: list[str], key: str) -> int | None:
    lowered = [h.strip().lower().replace(" ", "_") for h in headers]
    aliases = _HEADER_ALIASES[key]
    for i, h in enumerate(lowered):
        if h in aliases:
            return i
    return None


def read_assets(path: Path | str) -> list[Asset]:
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        rows = list(reader)
    if not rows:
        return []
    headers = rows[0]
    indices = {k: _col(headers, k) for k in _HEADER_ALIASES}
    out: list[Asset] = []
    for row in rows[1:]:
        if not row or all(not c.strip() for c in row):
            continue
        def get(key: str, row: list[str] = row) -> str:
            i = indices[key]
            if i is None or i >= len(row):
                return ""
            return row[i]
        asset_id = get("asset_id").strip() or f"row-{len(out)+1}"
        tags_raw = get("tags").strip()
        tags = [t.strip() for t in tags_raw.split(";") if t.strip()] if tags_raw else []
        out.append(
            Asset(
                asset_id=asset_id,
                name=get("name").strip() or asset_id,
                vendor=get("vendor").strip(),
                product=get("product").strip(),
                version=get("version").strip(),
                seat_count=max(1, _int(get("seat_count"))),
                owner=get("owner").strip(),
                contract_end_date=_date(get("contract_end_date")),
                feature_usage=get("feature_usage").strip().lower(),
                annual_spend=_float(get("annual_spend")),
                tags=tags,
            )
        )
    return out


def read_assets_from_text(text: str) -> list[Asset]:
    import os
    import tempfile

    fd, p = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        return read_assets(p)
    finally:
        Path(p).unlink(missing_ok=True)
