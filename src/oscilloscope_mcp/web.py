"""REST API for oscilloscope-mcp webapp."""

from __future__ import annotations

import json
import os
import time
from collections import deque
from typing import Any
from uuid import uuid4

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from oscilloscope_mcp import __version__
from oscilloscope_mcp.capabilities import build_capabilities
from oscilloscope_mcp.config import get_settings
from oscilloscope_mcp.services.registry import get_last_capture, get_session


class ActivityLog:
    def __init__(self, max_entries=2000):
        self.max_entries = max_entries
        self._entries = deque(maxlen=max_entries)

    def add(self, level, kind, detail, meta=None):
        eid = f"{time.time():.6f}.{uuid4().hex[:6]}"
        self._entries.append(
            {
                "id": eid,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                "level": level.upper(),
                "kind": kind,
                "detail": detail,
                "meta": meta or {},
            }
        )
        return eid

    def info(self, kind, detail, **meta):
        return self.add("INFO", kind, detail, meta)

    def warn(self, kind, detail, **meta):
        return self.add("WARNING", kind, detail, meta)

    def error(self, kind, detail, **meta):
        return self.add("ERROR", kind, detail, meta)

    def query(self, limit=50, offset=0, level=None, kind=None, search=None, sort="desc", after_id=None):
        entries = list(self._entries)
        if after_id:
            try:
                at = float(after_id.split(".")[0])
                entries = [e for e in entries if float(e["id"].split(".")[0]) > at]
            except:
                pass
        if level:
            lo = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
            ml = lo.get(level.upper(), 1)
            entries = [e for e in entries if lo.get(e["level"], 1) >= ml]
        if kind:
            entries = [e for e in entries if e["kind"] == kind]
        if search:
            q = search.lower()
            entries = [e for e in entries if q in e["detail"].lower()]
        entries.sort(key=lambda e: e["id"], reverse=(sort == "desc"))
        total = len(entries)
        page = entries[offset : offset + limit]
        return {
            "entries": page,
            "total": total,
            "limit": limit,
            "offset": offset,
            "max_entries": self.max_entries,
            "sort": sort,
        }

    def stats(self):
        levels, kinds = {}, {}
        for e in self._entries:
            levels[e["level"]] = levels.get(e["level"], 0) + 1
            kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
        return {"total": len(self._entries), "max_entries": self.max_entries, "levels": levels, "kinds": kinds}

    def clear(self):
        self._entries.clear()


_activity_log = ActivityLog()


def setup_webapp(app: FastAPI, mcp: Any) -> None:
    """Register REST routes on the FastAPI application."""

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "server": "oscilloscope-mcp"}

    @app.get("/api/logs")
    async def api_log_query(
        limit: int = 50,
        offset: int = 0,
        level: str = None,
        kind: str = None,
        search: str = None,
        sort: str = "desc",
        after_id: str = None,
    ):
        return _activity_log.query(
            limit=limit, offset=offset, level=level, kind=kind, search=search, sort=sort, after_id=after_id
        )

    @app.get("/api/logs/stats")
    async def api_log_stats():
        return _activity_log.stats()

    @app.post("/api/logs/clear")
    async def api_log_clear():
        _activity_log.clear()
        return {"success": True}

    @app.get("/api/status")
    async def api_status() -> dict[str, Any]:
        settings = get_settings()
        session = get_session()
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        backend = session.backend
        connected = None
        if backend is not None:
            device = await backend.get_connected_device()
            connected = device.model_dump(mode="json") if device else None
        return {
            "status": "ok",
            "version": __version__,
            "tool_count": len(tools),
            "tools": tool_names,
            "active_backend": session.backend_name,
            "connected_device": connected,
            "capture_dir": str(settings.capture_dir),
            "capabilities": {
                "prompts": True,
                "resources": True,
                "simulator": True,
                "picoscope": True,
                "hantek": True,
            },
        }

    @app.get("/api/capabilities")
    async def api_capabilities() -> dict[str, Any]:
        return await build_capabilities(mcp)

    @app.get("/api/tools")
    async def api_tools() -> dict[str, Any]:
        tools = await mcp.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "inputSchema": t.parameters,
                }
                for t in tools
            ]
        }

    @app.post("/api/tools/{name}/call", response_model=None)
    async def api_tool_call(name: str, body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        try:
            result = await mcp.call_tool(name, body.get("arguments", {}))
            content = result.content if hasattr(result, "content") else result
            if isinstance(content, list) and content:
                item = content[0]
                text = item.text if hasattr(item, "text") else str(item)
                try:
                    parsed = json.loads(text)
                    return {"success": True, "data": parsed}
                except (json.JSONDecodeError, TypeError):
                    return {"success": True, "data": text}
            return {"success": True, "data": content}
        except Exception as exc:
            return JSONResponse({"success": False, "message": str(exc)}, status_code=500)

    @app.get("/api/capture/last")
    async def api_capture_last() -> dict[str, Any]:
        capture = get_last_capture()
        if capture is None:
            return {"success": False, "message": "No capture in memory"}
        step = max(1, len(capture.time_s) // 500)
        return {
            "success": True,
            "data": {
                "capture": capture.model_dump(mode="json"),
                "preview": {
                    "step": step,
                    "time_s": capture.time_s[::step],
                    "channels": {ch.channel_id: ch.samples_v[::step] for ch in capture.channels},
                },
            },
        }

    @app.get("/api/llm/providers")
    async def llm_providers():
        OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                r = await c.get(f"{OLLAMA_BASE}/api/tags")
                r.raise_for_status()
                data = r.json()
                models = [m["name"] for m in data.get("models", [])]
        except Exception:
            models = []
        return {"providers": [{"name": "ollama", "models": models}]}

    @app.post("/api/llm/chat")
    async def llm_chat(body: dict):
        OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        prompt = body.get("prompt", "")
        model = body.get("model", "llama3.2:3b")
        if not prompt:
            return {"error": "Missing prompt"}
        try:
            async with httpx.AsyncClient(timeout=120) as c:
                r = await c.post(
                    f"{OLLAMA_BASE}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                )
                r.raise_for_status()
                data = r.json()
                return {"response": data.get("response", "")}
        except Exception as e:
            return {"error": str(e)}

    @app.post("/api/capture/run", response_model=None)
    async def api_capture_run(body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        args = {
            "operation": "single",
            "sample_rate_hz": body.get("sample_rate_hz", 100_000),
            "sample_count": body.get("sample_count", 2000),
            "channel_id": body.get("channel_id", "A"),
            "range_v": body.get("range_v", 2.0),
        }
        return await api_tool_call("scope_capture", {"arguments": args})
