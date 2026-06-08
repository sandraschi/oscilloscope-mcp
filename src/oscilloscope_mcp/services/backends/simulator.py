"""Simulator backend - always available for development and CI."""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from oscilloscope_mcp.models.capture import ChannelCapture, ChannelConfig, TriggerConfig, WaveformCapture
from oscilloscope_mcp.models.device import DeviceCapabilities, DeviceInfo
from oscilloscope_mcp.services.backends.base import OscilloscopeBackend


class SimulatorBackend(OscilloscopeBackend):
    """Generates synthetic waveforms without USB hardware."""

    name = "simulator"

    def __init__(self) -> None:
        self._connected_id: str | None = None
        self._channels: list[ChannelConfig] = [
            ChannelConfig(channel_id="A", enabled=True, range_v=2.0),
            ChannelConfig(channel_id="B", enabled=True, range_v=2.0),
        ]
        self._trigger = TriggerConfig()
        self._waveform = "sine"
        self._frequency_hz = 1000.0
        self._amplitude_v = 0.8

    async def list_devices(self) -> list[DeviceInfo]:
        caps = DeviceCapabilities(
            backend="simulator",
            channels=2,
            max_sample_rate_hz=10_000_000,
            bandwidth_hz=5_000_000,
            resolution_bits=12,
            has_awg=True,
            notes="Synthetic waveforms for development, CI, and agent dry-runs.",
        )
        return [
            DeviceInfo(
                device_id="sim-001",
                backend="simulator",
                model="Oscilloscope Simulator",
                serial="SIM000001",
                connected=self._connected_id == "sim-001",
                capabilities=caps,
                driver_status="available",
            )
        ]

    async def connect(self, device_id: str) -> DeviceInfo:
        devices = await self.list_devices()
        match = next((d for d in devices if d.device_id == device_id), None)
        if match is None:
            raise ValueError(f"Simulator device '{device_id}' not found")
        self._connected_id = device_id
        return match.model_copy(update={"connected": True})

    async def disconnect(self) -> None:
        self._connected_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._connected_id:
            return None
        devices = await self.list_devices()
        return next((d for d in devices if d.device_id == self._connected_id), None)

    async def configure_channels(self, channels: list[ChannelConfig]) -> list[ChannelConfig]:
        self._ensure_connected()
        self._channels = channels
        return channels

    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._ensure_connected()
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
        self._ensure_connected()
        active_channels = channels or [c for c in self._channels if c.enabled]
        if not active_channels:
            raise ValueError("At least one enabled channel is required")

        sample_rate_hz = max(100.0, min(sample_rate_hz, 10_000_000))
        sample_count = max(16, min(sample_count, 1_000_000))
        trigger = trigger or self._trigger

        dt = 1.0 / sample_rate_hz
        time_s = (np.arange(sample_count, dtype=np.float64) * dt).tolist()

        channel_captures: list[ChannelCapture] = []
        for index, cfg in enumerate(active_channels):
            samples = self._generate_samples(sample_count, dt, channel_index=index)
            channel_captures.append(
                ChannelCapture(
                    channel_id=cfg.channel_id,
                    samples_v=samples.tolist(),
                    range_v=cfg.range_v,
                    coupling=cfg.coupling,
                )
            )

        return WaveformCapture(
            backend=self.name,
            device_id=self._connected_id or "sim-001",
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            time_s=time_s,
            channels=channel_captures,
            trigger=trigger,
            metadata={
                "simulated": True,
                "waveform": self._waveform,
                "frequency_hz": self._frequency_hz,
                "amplitude_v": self._amplitude_v,
            },
        )

    async def get_status(self) -> dict[str, Any]:
        device = await self.get_connected_device()
        return {
            "backend": self.name,
            "connected": device is not None,
            "device_id": device.device_id if device else None,
            "waveform": self._waveform,
            "frequency_hz": self._frequency_hz,
            "amplitude_v": self._amplitude_v,
        }

    def set_simulation_profile(
        self,
        *,
        waveform: str = "sine",
        frequency_hz: float = 1000.0,
        amplitude_v: float = 0.8,
    ) -> None:
        """Adjust synthetic signal parameters (simulator only)."""
        self._waveform = waveform
        self._frequency_hz = frequency_hz
        self._amplitude_v = amplitude_v

    def _generate_samples(self, count: int, dt: float, *, channel_index: int) -> np.ndarray:
        t = np.arange(count, dtype=np.float64) * dt
        phase = channel_index * math.pi / 4
        freq = self._frequency_hz * (1.0 + 0.1 * channel_index)

        if self._waveform == "square":
            wave = np.sign(np.sin(2 * math.pi * freq * t + phase))
            return self._amplitude_v * wave
        if self._waveform == "ramp":
            return self._amplitude_v * (2 * ((freq * t) % 1.0) - 1.0)
        if self._waveform == "noise":
            rng = np.random.default_rng(42 + channel_index)
            return self._amplitude_v * rng.standard_normal(count)
        return self._amplitude_v * np.sin(2 * math.pi * freq * t + phase)

    def _ensure_connected(self) -> None:
        if not self._connected_id:
            raise RuntimeError("No simulator device connected. Use scope_device(operation='connect').")
