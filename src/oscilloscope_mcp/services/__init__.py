"""Service layer for oscilloscope-mcp."""

from .registry import clear_services, get_last_capture, get_session, set_last_capture

__all__ = ["clear_services", "get_last_capture", "get_session", "set_last_capture"]
