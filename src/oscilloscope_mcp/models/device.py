"""Device discovery and capability models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

BackendType = Literal["simulator", "picoscope", "hantek"]


class DeviceCapabilities(BaseModel):
    """Hardware capability summary for agent planning."""

    backend: BackendType
    channels: int = Field(ge=1, le=8)
    max_sample_rate_hz: float = Field(gt=0)
    bandwidth_hz: float | None = None
    resolution_bits: int = Field(ge=8, le=16, default=8)
    has_awg: bool = False
    has_logic_analyzer: bool = False
    max_input_voltage_v: float | None = None
    supported_couplings: list[str] = Field(default_factory=lambda: ["dc", "ac"])
    notes: str | None = None


class DeviceInfo(BaseModel):
    """Discovered oscilloscope device."""

    device_id: str
    backend: BackendType
    model: str
    serial: str | None = None
    connected: bool = False
    capabilities: DeviceCapabilities
    driver_status: str = "available"
    driver_hint: str | None = None
