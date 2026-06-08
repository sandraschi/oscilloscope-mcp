"""Configuration management for oscilloscope-mcp."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BackendPreference = Literal["auto", "simulator", "picoscope", "hantek"]


def _load_dotenv_files() -> None:
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parents[2] / ".env",
    ]
    for candidate in candidates:
        if candidate.exists():
            load_dotenv(candidate)
            return


class OscilloscopeSettings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="OSCILLOSCOPE_MCP_",
        env_file=None,
        extra="ignore",
    )

    backend: BackendPreference = "auto"
    device_id: str | None = None
    capture_dir: Path = Path("./captures")
    transport: Literal["stdio", "http", "sse"] = "stdio"
    host: str = "127.0.0.1"
    port: int = 10936
    webapp_port: int = 10937
    path: str = "/mcp"
    log_level: str = "INFO"

    @field_validator("capture_dir", mode="before")
    @classmethod
    def expand_capture_dir(cls, value: str | Path) -> Path:
        return Path(value).expanduser()

    @field_validator("port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        return max(1024, min(65535, value))


@lru_cache(maxsize=1)
def get_settings() -> OscilloscopeSettings:
    """Load settings once per process."""
    _load_dotenv_files()
    if os.getenv("OSCILLOSCOPE_ALLOW_LOGGING", "").lower() in ("1", "true", "yes"):
        pass
    return OscilloscopeSettings()
