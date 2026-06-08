"""scope_device portmanteau - discovery, connection, and status."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.config import get_settings
from oscilloscope_mcp.services.registry import get_session


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def scope_device(
    operation: Annotated[
        Literal["list", "connect", "disconnect", "status", "capabilities", "backends"],
        Field(description="Device management operation."),
    ],
    device_id: Annotated[
        str | None, Field(description="Device ID for connect (e.g. sim-001, picoscope:12345).")
    ] = None,
    backend: Annotated[str | None, Field(description="Force backend: simulator, picoscope, or hantek.")] = None,
) -> ToolResult:
    """Discover, connect, and manage USB oscilloscope devices.

    Consolidates device enumeration, session connection, backend selection, and health status.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - scope_device(operation="list")
    - scope_device(operation="connect", device_id="sim-001")
    - scope_device(operation="status")
    - scope_device(operation="backends")
    """
    session = get_session()
    settings = get_settings()

    try:
        if operation == "list":
            devices = await session.list_all_devices()
            data = {
                "devices": [d.model_dump(mode="json") for d in devices],
                "count": len(devices),
                "preferred_backend": settings.backend,
            }
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "backends":
            data = {"backends": session.list_backend_names(), "active": session.backend_name}
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "connect":
            if not device_id:
                raise ValueError("device_id is required for connect")
            device = await session.connect(device_id, backend=backend)
            data = device.model_dump(mode="json")
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "disconnect":
            await session.disconnect()
            return ToolResult(content={"success": True, "operation": operation, "data": {"connected": False}})

        if operation == "status":
            active = session.backend
            if active is None:
                data: dict[str, Any] = {"connected": False, "backend": None}
            else:
                status = await active.get_status()
                connected = await active.get_connected_device()
                data = {
                    "connected": connected is not None,
                    "backend": session.backend_name,
                    "device": connected.model_dump(mode="json") if connected else None,
                    "status": status,
                    "capture_dir": str(settings.capture_dir),
                }
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "capabilities":
            active = session.backend or await session.resolve_backend()
            connected = await active.get_connected_device()
            if connected:
                data = connected.capabilities.model_dump(mode="json")
            else:
                devices = await active.list_devices()
                data = devices[0].capabilities.model_dump(mode="json") if devices else {}
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
