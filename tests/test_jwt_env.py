"""JWT secret env fail-closed tests."""
import importlib
import os

import pytest

import rollover.auth.jwt as jwt_mod


def test_short_secret_raises_on_reload(monkeypatch: pytest.MonkeyPatch) -> None:
    original = os.environ.get("DEVFLOW_JWT_SECRET")
    try:
        monkeypatch.setenv("DEVFLOW_JWT_SECRET", "short")
        with pytest.raises(RuntimeError):
            importlib.reload(jwt_mod)
    finally:
        if original is None:
            monkeypatch.delenv("DEVFLOW_JWT_SECRET", raising=False)
        else:
            monkeypatch.setenv("DEVFLOW_JWT_SECRET", original)
        importlib.reload(jwt_mod)


def test_missing_secret_raises_on_reload(monkeypatch: pytest.MonkeyPatch) -> None:
    original = os.environ.get("DEVFLOW_JWT_SECRET")
    try:
        monkeypatch.delenv("DEVFLOW_JWT_SECRET", raising=False)
        with pytest.raises(RuntimeError):
            importlib.reload(jwt_mod)
    finally:
        monkeypatch.setenv("DEVFLOW_JWT_SECRET", original if original is not None else "x" * 64)
        importlib.reload(jwt_mod)


def test_password_72_byte_truncation() -> None:
    raw = "a" * 100
    h = jwt_mod.hash_password(raw)
    # truncated to 72 bytes should verify
    assert jwt_mod.verify_password("a" * 72, h) is True
    # different suffix beyond 72 should still verify (truncated)
    assert jwt_mod.verify_password("a" * 72 + "b", h) is True
