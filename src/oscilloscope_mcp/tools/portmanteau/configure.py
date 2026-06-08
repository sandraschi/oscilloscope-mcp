"""scope_configure portmanteau - channel and simulator settings."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.models.capture import ChannelConfig, Coupling
from oscilloscope_mcp.services.backends.simulator import SimulatorBackend
from oscilloscope_mcp.services.registry import get_session


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def scope_configure(
    operation: Annotated[
        Literal["channel", "channels", "get", "simulator_profile"],
        Field(description="Configuration operation."),
    ],
    channel_id: Annotated[str | None, Field(description="Channel label (A, B, CH1).")] = None,
    enabled: Annotated[bool | None, Field(description="Enable or disable channel.")] = None,
    range_v: Annotated[float | None, Field(description="Full-scale voltage range in volts.", gt=0)] = None,
    coupling: Annotated[Coupling | None, Field(description="Input coupling: dc or ac.")] = None,
    offset_v: Annotated[float | None, Field(description="Analog offset in volts.")] = None,
    waveform: Annotated[
        Literal["sine", "square", "ramp", "noise"] | None,
        Field(description="Simulator waveform type (simulator_profile only)."),
    ] = None,
    frequency_hz: Annotated[float | None, Field(description="Simulator frequency in Hz.", gt=0)] = None,
    amplitude_v: Annotated[float | None, Field(description="Simulator amplitude in volts.", gt=0)] = None,
) -> ToolResult:
    """Configure oscilloscope channels and simulator signal profiles.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - scope_configure(operation="channel", channel_id="A", range_v=2.0, coupling="dc")
    - scope_configure(operation="get")
    - scope_configure(operation="simulator_profile", waveform="square", frequency_hz=1000)
    """
    session = get_session()

    try:
        backend = session.backend
        if backend is None:
            backend = await session.resolve_backend()
            await backend.connect("sim-001" if backend.name == "simulator" else "auto")

        if operation == "simulator_profile":
            if not isinstance(backend, SimulatorBackend):
                raise ValueError("simulator_profile is only available on the simulator backend")
            backend.set_simulation_profile(
                waveform=waveform or "sine",
                frequency_hz=frequency_hz or 1000.0,
                amplitude_v=amplitude_v or 0.8,
            )
            status = await backend.get_status()
            return ToolResult(content={"success": True, "operation": operation, "data": status})

        if operation == "channel":
            if not channel_id:
                raise ValueError("channel_id is required for channel operation")
            cfg = ChannelConfig(
                channel_id=channel_id,
                enabled=True if enabled is None else enabled,
                range_v=range_v or 1.0,
                coupling=coupling or "dc",
                offset_v=offset_v or 0.0,
            )
            applied = await backend.configure_channels([cfg])
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": [c.model_dump(mode="json") for c in applied],
                }
            )

        if operation == "channels":
            if not channel_id:
                raise ValueError("channel_id is required for channels batch update")
            cfg = ChannelConfig(
                channel_id=channel_id,
                enabled=True if enabled is None else enabled,
                range_v=range_v or 1.0,
                coupling=coupling or "dc",
                offset_v=offset_v or 0.0,
            )
            applied = await backend.configure_channels([cfg])
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": [c.model_dump(mode="json") for c in applied],
                }
            )

        if operation == "get":
            device = await backend.get_connected_device()
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "backend": backend.name,
                        "device": device.model_dump(mode="json") if device else None,
                    },
                }
            )

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
