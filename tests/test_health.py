"""Smoke tests."""
from fastapi.testclient import TestClient

from rollover.app import create_app


def test_health() -> None:
    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": "0.1.0"}
