"""scope_help portmanteau - discovery and documentation."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.services.registry import get_session

_TOOLS_CATALOG: dict[str, dict[str, Any]] = {
    "scope_device": {
        "category": "device",
        "operations": ["list", "connect", "disconnect", "status", "capabilities", "backends"],
        "description": "Discover USB scopes, connect sessions, inspect backend health.",
    },
    "scope_configure": {
        "category": "configure",
        "operations": ["channel", "channels", "get", "simulator_profile"],
        "description": "Set voltage range, coupling, and simulator waveform parameters.",
    },
    "scope_trigger": {
        "category": "trigger",
        "operations": ["set", "get", "arm", "force"],
        "description": "Configure trigger source, threshold, edge, and mode.",
    },
    "scope_capture": {
        "category": "capture",
        "operations": ["single", "preview", "export_csv", "export_summary", "last"],
        "description": "Acquire waveforms and export CSV/JSON summaries.",
    },
    "scope_measure": {
        "category": "measure",
        "operations": ["all", "vpp", "frequency", "duty", "rise_time", "fresh"],
        "description": "Compute Vpp, frequency, duty cycle, and rise time.",
    },
    "scope_help": {
        "category": "help",
        "operations": ["discover", "tool_help", "status", "quickstart", "faq", "hardware_guide"],
        "description": "Tool discovery, quickstart, FAQ, and hardware buying guide.",
    },
}


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def scope_help(
    operation: Annotated[
        Literal["discover", "tool_help", "status", "quickstart", "faq", "hardware_guide"],
        Field(description="Help operation."),
    ],
    tool_name: Annotated[str | None, Field(description="Tool name for tool_help.")] = None,
    topic: Annotated[str | None, Field(description="FAQ topic filter.")] = None,
) -> ToolResult:
    """Help, discovery, and hardware guidance for oscilloscope-mcp.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - scope_help(operation="discover")
    - scope_help(operation="quickstart")
    - scope_help(operation="hardware_guide")
    """
    try:
        if operation == "discover":
            catalog = [{"name": name, **meta} for name, meta in _TOOLS_CATALOG.items()]
            if topic:
                catalog = [item for item in catalog if item["category"] == topic]
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": catalog,
                    "count": len(catalog),
                }
            )

        if operation == "tool_help":
            if not tool_name:
                raise ValueError("tool_name is required for tool_help")
            tool = _TOOLS_CATALOG.get(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {"name": tool_name, **tool},
                }
            )

        if operation == "status":
            session = get_session()
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "server": "oscilloscope-mcp",
                        "version": "0.1.0",
                        "tools_registered": len(_TOOLS_CATALOG),
                        "active_backend": session.backend_name,
                    },
                }
            )

        if operation == "quickstart":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "steps": [
                            "1. scope_device(operation='list')",
                            "2. scope_device(operation='connect', device_id='sim-001')",
                            "3. scope_configure(operation='channel', channel_id='A', range_v=2.0)",
                            "4. scope_trigger(operation='set', source_channel='A', threshold_v=0.0)",
                            "5. scope_capture(operation='single', sample_rate_hz=100000, sample_count=2000)",
                            "6. scope_measure(operation='all', channel_id='A')",
                            "7. scope_capture(operation='export_csv')",
                        ],
                    },
                }
            )

        if operation == "faq":
            faq = [
                {
                    "q": "Can I use this without hardware?",
                    "a": "Yes. Connect to sim-001 and use the simulator backend.",
                    "topic": "simulator",
                },
                {
                    "q": "Which USB scope is recommended?",
                    "a": "PicoScope 2204A for scope-only; Digilent Analog Discovery 3 for mixed-signal bench.",
                    "topic": "hardware",
                },
                {
                    "q": "Why does PicoScope fail to connect?",
                    "a": "Install PicoSDK from picotech.com and run: uv sync --extra picoscope",
                    "topic": "picoscope",
                },
                {
                    "q": "What is safe to probe?",
                    "a": "Low-voltage MCU rails and logic (under ~30 V). Never probe mains without proper HV probes.",
                    "topic": "safety",
                },
            ]
            if topic:
                faq = [item for item in faq if item["topic"] == topic]
            return ToolResult(content={"success": True, "operation": operation, "data": faq})

        if operation == "hardware_guide":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "recommendations": [
                            {
                                "tier": "best_value",
                                "model": "PicoScope 2204A",
                                "price_usd": "130-190",
                                "bandwidth": "10 MHz",
                                "backend": "picoscope",
                                "notes": "Official PicoSDK, pyPicoSDK, includes AWG.",
                            },
                            {
                                "tier": "swiss_army_knife",
                                "model": "Digilent Analog Discovery 3",
                                "price_usd": "200-400",
                                "bandwidth": "30+ MHz",
                                "backend": "planned: waveforms",
                                "notes": "Scope + logic + AWG + PSU. WaveForms SDK (future backend).",
                            },
                            {
                                "tier": "budget_hack",
                                "model": "Hantek 6022BE/BL",
                                "price_usd": "40-80",
                                "bandwidth": "~20 MHz",
                                "backend": "hantek",
                                "notes": "Open-source PyHT6022. 8-bit, dual USB on some models.",
                            },
                        ],
                        "avoid": "No-name AliExpress scopes with closed Windows-only apps and no SDK.",
                    },
                }
            )

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
