"""FastAPI application factory."""
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from .assets import read_assets_from_text
from .auth.dependencies import require_user
from .models import VendorUpgrade
from .registry import load_registry
from .report import render_markdown, render_pdf_bytes, render_text

API_VERSION = "0.1.0"


def create_app() -> FastAPI:
    app = FastAPI(title="rollover-auditor", version=API_VERSION)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    upgrades_cache: dict[str, list[VendorUpgrade]] = {}

    def _upgrades() -> list[VendorUpgrade]:
        if "all" not in upgrades_cache:
            upgrades_cache["all"] = load_registry()
        return upgrades_cache["all"]

    @app.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": API_VERSION}

    @app.get("/registry", tags=["registry"])
    async def registry() -> list[dict[str, object]]:
        return [
            {
                "vendor": u.vendor,
                "product_from": u.product_from,
                "product_to": u.product_to,
                "enforced_date": u.enforced_date.isoformat() if u.enforced_date else None,
                "deflection_strategy": u.deflection_strategy,
                "typical_cost_formula": u.typical_cost_formula,
                "impact_estimate": u.impact_estimate,
            }
            for u in _upgrades()
        ]

    @app.post("/report", tags=["report"])
    async def report(request: Request, format: str = "markdown") -> dict[str, object]:
        body = (await request.body()).decode("utf-8", errors="replace")
        if not body.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty csv body")
        assets = read_assets_from_text(body)
        upgrades = _upgrades()
        md = render_markdown(assets, upgrades)
        if format == "text":
            return {"format": "text", "content": render_text(md)}
        if format == "pdf":
            return {"format": "pdf", "bytes": len(render_pdf_bytes(md))}
        return {"format": "markdown", "content": md}

    @app.get("/me", tags=["auth"])
    async def me(payload: Annotated[dict[str, str], Depends(require_user)]) -> dict[str, str]:
        return {"sub": str(payload["sub"])}

    return app


app = create_app()
