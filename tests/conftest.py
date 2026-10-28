"""Test environment defaults."""
import os

os.environ.setdefault("DEVFLOW_JWT_SECRET", "x" * 64)
