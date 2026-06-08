"""oscilloscope-mcp FastMCP 3.2+ server entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from oscilloscope_mcp import __version__
from oscilloscope_mcp.app import mcp
from oscilloscope_mcp.utils.logger import get_logger
from oscilloscope_mcp.web import setup_webapp

logger = get_logger(__name__)

from oscilloscope_mcp.tools import portmanteau  # noqa: F401, E402

_mcp_asgi = mcp.http_app(path="/")

app = FastAPI(title="OscilloscopeMCP", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
setup_webapp(app, mcp)
app.mount("/mcp", _mcp_asgi)


def main() -> None:
    """Main entry point - supports STDIO, HTTP, and SSE transport."""
    from oscilloscope_mcp.transport import run_server

    logger.info("Starting oscilloscope-mcp (FastMCP 3.2+)")
    run_server(mcp, server_name="oscilloscope-mcp")


if __name__ == "__main__":
    main()
