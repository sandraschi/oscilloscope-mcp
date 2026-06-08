"""Hantek 6022BE/BL backend via PyHT6022 (optional extra)."""

from __future__ import annotations

from typing import Any

import numpy as np

from oscilloscope_mcp.models.capture import ChannelCapture, ChannelConfig, TriggerConfig, WaveformCapture
from oscilloscope_mcp.models.device import DeviceCapabilities, DeviceInfo
from oscilloscope_mcp.services.backends.base import OscilloscopeBackend


class HantekBackend(OscilloscopeBackend):
    """Hantek 6022 USB oscilloscope backend."""

    name = "hantek"

    def __init__(self) -> None:
        self._scope: Any | None = None
        self._device_id: str | None = None
        self._channels: list[ChannelConfig] = []
        self._trigger = TriggerConfig()

    def _import_scope(self) -> Any:
        try:
            from PyHT6022.LibUsbScope import Oscilloscope  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "Hantek support is not installed. Run: uv sync --extra hantek "
                "and install OpenHantek firmware/driver prerequisites."
            ) from exc
        return Oscilloscope()

    async def list_devices(self) -> list[DeviceInfo]:
        caps = DeviceCapabilities(
            backend="hantek",
            channels=2,
            max_sample_rate_hz=48_000_000,
            bandwidth_hz=20_000_000,
            resolution_bits=8,
            max_input_voltage_v=35.0,
            notes="Hantek 6022BE/BL family. Requires libusb and custom firmware.",
        )
        return [
            DeviceInfo(
                device_id="hantek:6022",
                backend="hantek",
                model="Hantek 6022BE/BL",
                connected=self._scope is not None,
                capabilities=caps,
                driver_status="available",
                driver_hint="Use Zadig WinUSB on Windows or udev rules on Linux.",
            )
        ]

    async def connect(self, device_id: str) -> DeviceInfo:
        await self.disconnect()
        scope = self._import_scope()
        scope.setup()
        scope.open_handle()
        if not scope.is_device_firmware_present():
            scope.flash_firmware()
        self._scope = scope
        self._device_id = device_id
        devices = await self.list_devices()
        return next(d.model_copy(update={"connected": True}) for d in devices if d.device_id == device_id)

    async def disconnect(self) -> None:
        self._scope = None
        self._device_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._scope:
            return None
        devices = await self.list_devices()
        return next((d.model_copy(update={"connected": True}) for d in devices), None)

    async def configure_channels(self, channels: list[ChannelConfig]) -> list[ChannelConfig]:
        self._ensure_scope()
        self._channels = channels
        return channels

    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._ensure_scope()
        self._trigger = trigger
        return trigger

    async def capture_block(
        self,
        *,
        sample_rate_hz: float,
        sample_count: int,
        channels: list[ChannelConfig] | None = None,
        trigger: TriggerConfig | None = None,
    ) -> WaveformCapture:
        self._ensure_scope()
        active = channels or self._channels or [ChannelConfig(channel_id="CH1")]
        sample_count = max(16, min(sample_count, 65536))
        sample_rate_hz = max(1_000.0, min(sample_rate_hz, 3_000_000))

        raw = self._scope.read_samples(sample_count)
        arr = np.asarray(raw, dtype=np.float64)
        arrays = (
            [arr]
            if arr.ndim == 1
            else [arr[:, idx] for idx in range(min(arr.shape[1], len(active)))]
        )

        dt = 1.0 / sample_rate_hz
        time_s = (np.arange(sample_count, dtype=np.float64) * dt).tolist()

        channel_captures: list[ChannelCapture] = []
        for idx, cfg in enumerate(active[: len(arrays)]):
            volts = self._adc_to_volts(arrays[idx], cfg.range_v)
            channel_captures.append(
                ChannelCapture(
                    channel_id=cfg.channel_id,
                    samples_v=volts.tolist(),
                    range_v=cfg.range_v,
                    coupling=cfg.coupling,
                )
            )

        return WaveformCapture(
            backend=self.name,
            device_id=self._device_id or "hantek:6022",
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            time_s=time_s,
            channels=channel_captures,
            trigger=trigger or self._trigger,
            metadata={"driver": "PyHT6022"},
        )

    async def get_status(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            "connected": self._scope is not None,
            "device_id": self._device_id,
        }

    def _adc_to_volts(self, samples: np.ndarray, range_v: float) -> np.ndarray:
        """Map 8-bit ADC counts to volts for the configured range."""
        normalized = (samples - 128.0) / 128.0
        return normalized * (range_v / 2.0)

    def _ensure_scope(self) -> None:
        if self._scope is None:
            raise RuntimeError("No Hantek device connected. Use scope_device(operation='connect').")
