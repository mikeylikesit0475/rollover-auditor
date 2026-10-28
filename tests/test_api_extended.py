"""Extended API/registry endpoint tests."""
from fastapi.testclient import TestClient

from rollover.app import create_app


def test_registry_endpoint_shape() -> None:
    client = TestClient(create_app())
    r = client.get("/registry")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 8
    for entry in data:
        assert set(entry.keys()) >= {"vendor", "product_from", "deflection_strategy"}
        assert "product_to" in entry
        assert "enforced_date" in entry


def test_report_get_405() -> None:
    client = TestClient(create_app())
    r = client.get("/report")
    assert r.status_code == 405


def test_report_post_empty_400() -> None:
    client = TestClient(create_app())
    r = client.post("/report", content="   ")
    assert r.status_code == 400


def test_report_format_text() -> None:
    client = TestClient(create_app())
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    r = client.post("/report?format=text", content=csv_text)
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "text"
    assert "Rollover Audit Report" in body["content"]


def test_report_format_pdf() -> None:
    client = TestClient(create_app())
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    r = client.post("/report?format=pdf", content=csv_text)
    assert r.status_code == 200
    body = r.json()
    assert body["format"] == "pdf"
    assert isinstance(body["bytes"], int)
    assert body["bytes"] > 0


def test_report_markdown_counts() -> None:
    client = TestClient(create_app())
    csv_text = "asset_id,vendor,product\na1,Microsoft,Microsoft 365 E5\n"
    r = client.post("/report", content=csv_text)
    assert r.status_code == 200
    content = r.json()["content"]
    assert "# Rollover Audit Report" in content
    assert "Assets: 1" in content
    assert "HIGH:" in content or "HIGH" in content
