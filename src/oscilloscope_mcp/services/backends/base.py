"""Abstract oscilloscope backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from oscilloscope_mcp.models.capture import ChannelConfig, TriggerConfig, WaveformCapture
from oscilloscope_mcp.models.device import DeviceInfo


class OscilloscopeBackend(ABC):
    """Backend contract implemented by simulator, PicoScope, and Hantek drivers."""

    name: str

    @abstractmethod
    async def list_devices(self) -> list[DeviceInfo]:
        """Enumerate devices visible to this backend."""

    @abstractmethod
    async def connect(self, device_id: str) -> DeviceInfo:
        """Open a device session."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close the active device session."""

    @abstractmethod
    async def get_connected_device(self) -> DeviceInfo | None:
        """Return the currently connected device, if any."""

    @abstractmethod
    async def configure_channels(self, channels: list[ChannelConfig]) -> list[ChannelConfig]:
        """Apply channel settings."""

    @abstractmethod
    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        """Apply trigger settings."""

    @abstractmethod
    async def capture_block(
        self,
        *,
        sample_rate_hz: float,
        sample_count: int,
        channels: list[ChannelConfig] | None = None,
        trigger: TriggerConfig | None = None,
    ) -> WaveformCapture:
        """Perform a single block (snapshot) acquisition."""

    @abstractmethod
    async def get_status(self) -> dict[str, str | int | float | bool | None]:
        """Return backend health and session status."""
