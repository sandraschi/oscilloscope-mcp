"""Pytest fixtures for oscilloscope-mcp."""

import pytest

from oscilloscope_mcp.services import registry


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset global session state between tests."""
    registry._session = None  # type: ignore[attr-defined]
    registry._last_capture = None  # type: ignore[attr-defined]
    yield
    registry._session = None  # type: ignore[attr-defined]
    registry._last_capture = None  # type: ignore[attr-defined]
