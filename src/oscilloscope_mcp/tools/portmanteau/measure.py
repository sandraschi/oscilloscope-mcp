"""scope_measure portmanteau - waveform measurements."""

from __future__ import annotations

from typing import Annotated, Literal

import numpy as np
from fastmcp.tools import ToolResult
from pydantic import Field

from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.models.capture import ChannelConfig
from oscilloscope_mcp.services.registry import get_last_capture, get_session, set_last_capture
from oscilloscope_mcp.utils.measurements import compute_measurements


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True, "destructiveHint": False})
async def scope_measure(
    operation: Annotated[
        Literal["all", "vpp", "frequency", "duty", "rise_time", "fresh"],
        Field(description="Measurement operation."),
    ],
    channel_id: Annotated[str, Field(description="Channel to measure.")] = "A",
    sample_rate_hz: Annotated[float, Field(description="Sample rate for fresh capture.", gt=0)] = 100_000,
    sample_count: Annotated[int, Field(description="Samples for fresh capture.", ge=16, le=1_000_000)] = 4000,
) -> ToolResult:
    """Measure voltage and timing parameters from captured waveforms.

    Uses the last capture by default. Operation 'fresh' performs a new capture first.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - scope_measure(operation="all", channel_id="A")
    - scope_measure(operation="frequency", channel_id="A")
    - scope_measure(operation="fresh", sample_rate_hz=200000)
    """
    session = get_session()

    try:
        if operation == "fresh":
            backend = session.backend
            if backend is None:
                backend = await session.resolve_backend()
                await backend.connect("sim-001" if backend.name == "simulator" else "auto")
            capture = await backend.capture_block(
                sample_rate_hz=sample_rate_hz,
                sample_count=sample_count,
                channels=[ChannelConfig(channel_id=channel_id, enabled=True, range_v=2.0)],
            )
            set_last_capture(capture)
        else:
            capture = get_last_capture()
            if capture is None:
                raise RuntimeError("No capture available. Run scope_capture(operation='single') first.")

        channel = next((ch for ch in capture.channels if ch.channel_id == channel_id), None)
        if channel is None:
            raise ValueError(f"Channel '{channel_id}' not found in last capture")

        samples = np.asarray(channel.samples_v, dtype=np.float64)
        time_s = np.asarray(capture.time_s, dtype=np.float64)
        metrics = compute_measurements(samples, time_s)

        if operation == "vpp":
            data = {"v_pp_v": metrics["v_pp_v"], "v_min_v": metrics["v_min_v"], "v_max_v": metrics["v_max_v"]}
        elif operation == "frequency":
            data = {"frequency_hz": metrics.get("frequency_hz"), "period_s": metrics.get("period_s")}
        elif operation == "duty":
            data = {"duty_cycle_pct": metrics.get("duty_cycle_pct")}
        elif operation == "rise_time":
            data = {"rise_time_s": metrics.get("rise_time_s")}
        else:
            data = metrics

        return ToolResult(
            content={
                "success": True,
                "operation": operation,
                "data": data,
                "channel_id": channel_id,
            }
        )
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
