"""Shared FastMCP instance for oscilloscope-mcp."""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.prompts import Message

from oscilloscope_mcp.config import get_settings
from oscilloscope_mcp.services.registry import clear_services, get_last_capture, get_session
from oscilloscope_mcp.utils.logger import get_logger

if os.name == "nt":
    try:
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        pass

_is_stdio_mode = not sys.stdout.isatty()
if os.getenv("OSCILLOSCOPE_ALLOW_LOGGING", "").lower() in ("1", "true", "yes") or any(
    "pytest" in (arg or "") for arg in sys.argv
):
    _is_stdio_mode = False


@asynccontextmanager
async def _scope_lifespan(app):
    """FastMCP lifespan hook - startup probe and clean shutdown."""
    logger = get_logger(__name__)
    settings = get_settings()
    session = get_session()

    try:
        backend = await session.resolve_backend()
        devices = await backend.list_devices()
        logger.info(
            "Startup probe: backend=%s devices=%d capture_dir=%s",
            backend.name,
            len(devices),
            settings.capture_dir,
        )
        settings.capture_dir.mkdir(parents=True, exist_ok=True)
        app.state.settings = settings
        app.state.session = session
    except Exception as exc:
        logger.warning("Startup probe failed (simulator fallback may still work): %s", exc)

    yield

    await clear_services()
    app.state.session = None


mcp = FastMCP(
    "OscilloscopeMCP",
    instructions=(
        "OscilloscopeMCP is a FastMCP 3.2+ server for USB PC oscilloscopes (screenless frontends). "
        "Portmanteau tools: scope_device, scope_configure, scope_capture, scope_trigger, scope_measure, scope_help. "
        "Backends: simulator (always available), picoscope (pyPicoSDK + PicoSDK), hantek (PyHT6022 + libusb). "
        "Default workflow: scope_device(operation='list') -> connect -> configure -> capture -> measure. "
        "Resources: resource://scope/capabilities, resource://scope/quickstart, resource://scope/last_capture."
    ),
    lifespan=_scope_lifespan,
    on_duplicate="replace",
    strict_input_validation=True,
)


@mcp.resource("resource://scope/capabilities")
def scope_capabilities_resource() -> str:
    return """# oscilloscope-mcp capabilities

## Tools
- scope_device: list, connect, disconnect, status, capabilities, backends
- scope_configure: channel, timebase, coupling, range, simulator_profile
- scope_trigger: set, get, arm, force
- scope_capture: single, export_csv, export_summary, preview
- scope_measure: vpp, frequency, duty, rise_time, all (from last capture or fresh)
- scope_help: discover, tool_help, status, quickstart, faq, hardware_guide

## Backends
| Backend | Hardware | Python extra |
|---------|----------|--------------|
| simulator | none | (built-in) |
| picoscope | PicoScope 2000/3000/5000/6000 USB | --extra picoscope + PicoSDK |
| hantek | Hantek 6022BE/BL | --extra hantek + libusb |

## Safety
- Never probe mains or unknown high voltage without proper attenuation.
- Budget USB scopes are typically 35-50 V max on BNC inputs.
"""


@mcp.resource("resource://scope/quickstart")
def scope_quickstart_resource() -> str:
    return """# oscilloscope-mcp quickstart

1. scope_help(operation="quickstart")
2. scope_device(operation="list")
3. scope_device(operation="connect", device_id="sim-001")
4. scope_configure(operation="channel", channel_id="A", range_v=2.0, coupling="dc")
5. scope_trigger(operation="set", source_channel="A", threshold_v=0.0, mode="auto")
6. scope_capture(operation="single", sample_rate_hz=100000, sample_count=2000)
7. scope_measure(operation="all", channel_id="A")
8. scope_capture(operation="export_csv")
"""


@mcp.resource("resource://scope/last_capture")
def scope_last_capture_resource() -> str:
    capture = get_last_capture()
    if capture is None:
        return json.dumps({"status": "empty", "message": "No capture yet. Run scope_capture(operation='single')."})
    preview_step = max(1, len(capture.time_s) // 200)
    payload = {
        "status": "ok",
        "backend": capture.backend,
        "device_id": capture.device_id,
        "sample_rate_hz": capture.sample_rate_hz,
        "sample_count": capture.sample_count,
        "channels": [ch.channel_id for ch in capture.channels],
        "preview": {
            "step": preview_step,
            "time_s": capture.time_s[::preview_step],
            "channels": {ch.channel_id: ch.samples_v[::preview_step] for ch in capture.channels},
        },
    }
    return json.dumps(payload, indent=2)


@mcp.prompt()
def scope_bringup_guide() -> list[Message]:
    """Guide for oscilloscope bring-up and first capture."""
    return [
        Message(
            "Use scope_device(operation='list') to find USB scopes. "
            "For dry-runs without hardware, connect to sim-001. "
            "After capture, scope_measure(operation='all') returns frequency and Vpp.",
            role="user",
        )
    ]


if _is_stdio_mode:
    import logging

    logging.basicConfig(
        level=get_settings().log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
