"""Auth tests."""
from fastapi.testclient import TestClient

from rollover.app import create_app
from rollover.auth.jwt import create_access_token


def test_me_requires_token() -> None:
    client = TestClient(create_app())
    assert client.get("/me").status_code == 401


def test_me_with_token() -> None:
    client = TestClient(create_app())
    token = create_access_token("alice")
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"sub": "alice"}


def test_report_endpoint() -> None:
    client = TestClient(create_app())
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    r = client.post("/report", content=csv_text)
    assert r.status_code == 200
    assert r.json()["format"] == "markdown"
    assert "Rollover Audit Report" in r.json()["content"]
