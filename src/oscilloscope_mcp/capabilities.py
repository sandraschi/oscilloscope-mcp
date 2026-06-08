"""Build /api/capabilities from the mounted FastMCP instance."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from oscilloscope_mcp import __version__


async def build_capabilities(mcp: Any) -> dict[str, Any]:
    tool_names: list[str] = []
    try:
        tools = await mcp.list_tools(run_middleware=False)
        tool_names = sorted({t.name for t in tools})
    except Exception:
        tool_names = ["scope_help"]

    portmanteau_tools = [n for n in tool_names if n.startswith("scope_")]
    atomic_tools = [n for n in tool_names if n not in portmanteau_tools]

    prompt_names: list[str] = []
    try:
        prompts = await mcp.list_prompts()
        prompt_names = sorted({p.name for p in prompts})
    except Exception:
        prompt_names = []

    resource_uris: list[str] = []
    try:
        resources = await mcp.list_resources()
        for resource in resources:
            raw = getattr(resource, "uri", None) or getattr(resource, "name", "")
            uri = str(raw) if raw else ""
            if uri:
                resource_uris.append(uri)
    except Exception:
        resource_uris = [
            "resource://scope/capabilities",
            "resource://scope/quickstart",
            "resource://scope/last_capture",
        ]

    local_llm = False
    try:
        async with httpx.AsyncClient(timeout=1.2) as client:
            ollama = await client.get("http://127.0.0.1:11434/api/tags")
            local_llm = ollama.status_code < 500
    except Exception:
        local_llm = False

    return {
        "status": "ok",
        "server": {"name": "oscilloscope-mcp", "version": __version__, "fastmcp": "3.2+"},
        "tool_surface": {
            "total": len(tool_names),
            "portmanteau_count": len(portmanteau_tools),
            "atomic_count": len(atomic_tools),
            "portmanteau_tools": portmanteau_tools,
            "atomic_tools": atomic_tools,
        },
        "features": {
            "sampling": False,
            "agentic_workflows": False,
            "prompts": len(prompt_names) > 0,
            "resources": len(resource_uris) > 0,
            "skills": False,
            "local_llm": local_llm,
            "simulator_backend": True,
            "picoscope_backend": True,
            "hantek_backend": True,
            "waveform_viewer": True,
        },
        "inventory": {
            "workflow_tools": [],
            "prompt_names": prompt_names,
            "resource_uris": sorted(resource_uris),
            "skill_uris": [],
        },
        "runtime": {
            "transport": "http",
            "surface_mode": "portmanteau",
            "backend_port": 10936,
            "frontend_port": 10937,
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
