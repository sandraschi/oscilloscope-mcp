"""scope_trigger portmanteau - trigger configuration."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.models.capture import TriggerConfig, TriggerEdge, TriggerMode
from oscilloscope_mcp.services.registry import get_session

_trigger_state = TriggerConfig()


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def scope_trigger(
    operation: Annotated[
        Literal["set", "get", "arm", "force"],
        Field(description="Trigger operation."),
    ],
    source_channel: Annotated[str | None, Field(description="Trigger source channel.")] = None,
    threshold_v: Annotated[float | None, Field(description="Trigger threshold in volts.")] = None,
    mode: Annotated[TriggerMode | None, Field(description="Trigger mode: auto, normal, single, off.")] = None,
    edge: Annotated[TriggerEdge | None, Field(description="Trigger edge: rising or falling.")] = None,
) -> ToolResult:
    """Configure and inspect oscilloscope trigger settings.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - scope_trigger(operation="set", source_channel="A", threshold_v=0.5, mode="auto", edge="rising")
    - scope_trigger(operation="get")
    """
    global _trigger_state
    session = get_session()

    try:
        backend = session.backend
        if backend is None:
            raise RuntimeError("No device connected. Use scope_device(operation='connect') first.")

        if operation == "set":
            _trigger_state = TriggerConfig(
                mode=mode or _trigger_state.mode,
                source_channel=source_channel or _trigger_state.source_channel,
                threshold_v=threshold_v if threshold_v is not None else _trigger_state.threshold_v,
                edge=edge or _trigger_state.edge,
            )
            applied = await backend.configure_trigger(_trigger_state)
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": applied.model_dump(mode="json"),
                }
            )

        if operation == "get":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": _trigger_state.model_dump(mode="json"),
                }
            )

        if operation == "arm":
            _trigger_state = _trigger_state.model_copy(update={"mode": "normal"})
            applied = await backend.configure_trigger(_trigger_state)
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": applied.model_dump(mode="json"),
                    "message": "Trigger armed (normal mode).",
                }
            )

        if operation == "force":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": _trigger_state.model_dump(mode="json"),
                    "message": "Software force trigger acknowledged. Run scope_capture next.",
                }
            )

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
