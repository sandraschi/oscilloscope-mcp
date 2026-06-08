"""Global service registry for oscilloscope session state."""

from __future__ import annotations

from oscilloscope_mcp.models.capture import WaveformCapture
from oscilloscope_mcp.services.backends.base import OscilloscopeBackend
from oscilloscope_mcp.services.session import ScopeSession

_session: ScopeSession | None = None
_last_capture: WaveformCapture | None = None


def get_session() -> ScopeSession:
    """Return the active scope session, creating one if needed."""
    global _session
    if _session is None:
        _session = ScopeSession()
    return _session


def set_last_capture(capture: WaveformCapture) -> None:
    """Store the most recent capture for measure/export tools."""
    global _last_capture
    _last_capture = capture


def get_last_capture() -> WaveformCapture | None:
    """Return the most recent capture."""
    return _last_capture


def get_active_backend() -> OscilloscopeBackend | None:
    """Return the backend currently selected in the session."""
    return get_session().backend


async def clear_services() -> None:
    """Disconnect and reset session state (lifespan shutdown)."""
    global _session, _last_capture
    if _session is not None:
        await _session.disconnect()
    _session = None
    _last_capture = None
