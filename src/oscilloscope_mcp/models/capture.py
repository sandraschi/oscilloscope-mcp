"""Waveform capture models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Coupling = Literal["dc", "ac"]
TriggerMode = Literal["auto", "normal", "single", "off"]
TriggerEdge = Literal["rising", "falling"]


class ChannelConfig(BaseModel):
    """Per-channel oscilloscope configuration."""

    channel_id: str = Field(description="Channel label, e.g. A, B, CH1")
    enabled: bool = True
    range_v: float = Field(default=1.0, gt=0, description="Full-scale range in volts (e.g. 1.0 = +/-1 V)")
    coupling: Coupling = "dc"
    offset_v: float = 0.0


class TriggerConfig(BaseModel):
    """Trigger configuration."""

    mode: TriggerMode = "auto"
    source_channel: str = "A"
    threshold_v: float = 0.0
    edge: TriggerEdge = "rising"
    holdoff_s: float = 0.0


class ChannelCapture(BaseModel):
    """Captured samples for one channel."""

    channel_id: str
    samples_v: list[float]
    range_v: float
    coupling: Coupling = "dc"


class WaveformCapture(BaseModel):
    """Complete capture result returned to agents."""

    backend: str
    device_id: str
    sample_rate_hz: float
    sample_count: int
    time_s: list[float]
    channels: list[ChannelCapture]
    trigger: TriggerConfig | None = None
    pre_trigger_ratio: float = 0.0
    metadata: dict[str, str | float | int | bool] = Field(default_factory=dict)
