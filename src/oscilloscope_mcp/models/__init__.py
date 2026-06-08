"""Pydantic models for oscilloscope-mcp."""

from .capture import ChannelCapture, TriggerConfig, WaveformCapture
from .device import DeviceCapabilities, DeviceInfo

__all__ = [
    "ChannelCapture",
    "DeviceCapabilities",
    "DeviceInfo",
    "TriggerConfig",
    "WaveformCapture",
]
