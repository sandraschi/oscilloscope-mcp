"""PicoScope backend via pyPicoSDK (optional extra)."""

from __future__ import annotations

from typing import Any

from oscilloscope_mcp.models.capture import ChannelCapture, ChannelConfig, TriggerConfig, WaveformCapture
from oscilloscope_mcp.models.device import DeviceCapabilities, DeviceInfo
from oscilloscope_mcp.services.backends.base import OscilloscopeBackend


class PicoScopeBackend(OscilloscopeBackend):
    """PicoScope USB oscilloscope backend."""

    name = "picoscope"

    def __init__(self) -> None:
        self._scope: Any | None = None
        self._device_id: str | None = None
        self._model: str = "PicoScope"
        self._channels: list[ChannelConfig] = []
        self._trigger = TriggerConfig()
        self._driver_error: str | None = None
        self._psdk: Any | None = None

    def _import_psdk(self) -> Any:
        if self._psdk is not None:
            return self._psdk
        try:
            import pypicosdk as psdk  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError(
                "pyPicoSDK is not installed. Run: uv sync --extra picoscope "
                "and install PicoSDK from https://www.picotech.com/downloads"
            ) from exc
        self._psdk = psdk
        return psdk

    async def list_devices(self) -> list[DeviceInfo]:
        self._import_psdk()
        devices: list[DeviceInfo] = []
        try:
            from picosdk.discover import find_all_units  # type: ignore[import-not-found]

            for unit in find_all_units():
                info = getattr(unit, "info", None) or {}
                serial = str(info.get("serial", "unknown"))
                model = str(info.get("variant", info.get("model", "PicoScope")))
                device_id = f"picoscope:{serial}"
                devices.append(
                    DeviceInfo(
                        device_id=device_id,
                        backend="picoscope",
                        model=model,
                        serial=serial,
                        connected=self._device_id == device_id,
                        capabilities=DeviceCapabilities(
                            backend="picoscope",
                            channels=2,
                            max_sample_rate_hz=100_000_000,
                            bandwidth_hz=10_000_000,
                            resolution_bits=12,
                            has_awg=True,
                            max_input_voltage_v=50.0,
                            notes="Capabilities vary by model; verify against PicoScope datasheet.",
                        ),
                        driver_status="available",
                    )
                )
        except Exception as exc:
            self._driver_error = str(exc)
            devices.append(
                DeviceInfo(
                    device_id="picoscope:auto",
                    backend="picoscope",
                    model="PicoScope (auto-detect)",
                    connected=bool(self._scope),
                    capabilities=DeviceCapabilities(
                        backend="picoscope",
                        channels=2,
                        max_sample_rate_hz=100_000_000,
                        bandwidth_hz=10_000_000,
                        resolution_bits=12,
                        has_awg=True,
                    ),
                    driver_status="probe_failed",
                    driver_hint=str(exc),
                )
            )
        return devices

    async def connect(self, device_id: str) -> DeviceInfo:
        psdk = self._import_psdk()
        await self.disconnect()
        scope = self._open_scope_class(psdk)
        scope.open_unit()
        self._scope = scope
        self._device_id = device_id
        self._model = device_id.replace("picoscope:", "")
        caps = DeviceCapabilities(
            backend="picoscope",
            channels=2,
            max_sample_rate_hz=100_000_000,
            bandwidth_hz=10_000_000,
            resolution_bits=12,
            has_awg=True,
        )
        return DeviceInfo(
            device_id=device_id,
            backend="picoscope",
            model=self._model,
            serial=self._model,
            connected=True,
            capabilities=caps,
        )

    async def disconnect(self) -> None:
        if self._scope is not None:
            try:
                self._scope.close_unit()
            except Exception:
                pass
        self._scope = None
        self._device_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._scope or not self._device_id:
            return None
        devices = await self.list_devices()
        return next((d for d in devices if d.device_id == self._device_id), None)

    async def configure_channels(self, channels: list[ChannelConfig]) -> list[ChannelConfig]:
        self._ensure_scope()
        psdk = self._import_psdk()
        self._channels = channels
        for cfg in channels:
            if not cfg.enabled:
                continue
            channel_enum = self._channel_to_enum(psdk, cfg.channel_id)
            range_enum = self._range_to_enum(psdk, cfg.range_v)
            self._scope.set_channel(channel=channel_enum, range=range_enum)
        return channels

    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._ensure_scope()
        psdk = self._import_psdk()
        self._trigger = trigger
        channel_enum = self._channel_to_enum(psdk, trigger.source_channel)
        auto_trigger = 1 if trigger.mode in ("auto", "off") else 0
        threshold_mv = int(trigger.threshold_v * 1000)
        self._scope.set_simple_trigger(
            channel=channel_enum,
            threshold=threshold_mv,
            auto_trigger=auto_trigger,
        )
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
        psdk = self._import_psdk()
        active = channels or self._channels
        if trigger:
            await self.configure_trigger(trigger)

        sample_rate_msps = max(0.001, sample_rate_hz / 1_000_000)
        timebase = self._scope.sample_rate_to_timebase(
            sample_rate=sample_rate_msps,
            unit=psdk.SAMPLE_RATE.MSPS,
        )
        buffer, time_axis = self._scope.run_simple_block_capture(timebase, sample_count)

        time_s = time_axis.tolist() if hasattr(time_axis, "tolist") else list(time_axis)
        channel_captures: list[ChannelCapture] = []
        if isinstance(buffer, dict):
            for cfg in active:
                if not cfg.enabled:
                    continue
                samples = buffer.get(cfg.channel_id, buffer.get(cfg.channel_id.lower()))
                if samples is None:
                    continue
                volts = samples.tolist() if hasattr(samples, "tolist") else list(samples)
                channel_captures.append(
                    ChannelCapture(
                        channel_id=cfg.channel_id,
                        samples_v=volts,
                        range_v=cfg.range_v,
                        coupling=cfg.coupling,
                    )
                )
        else:
            volts = buffer.tolist() if hasattr(buffer, "tolist") else list(buffer)
            primary = active[0]
            channel_captures.append(
                ChannelCapture(
                    channel_id=primary.channel_id,
                    samples_v=volts,
                    range_v=primary.range_v,
                    coupling=primary.coupling,
                )
            )

        return WaveformCapture(
            backend=self.name,
            device_id=self._device_id or "picoscope:unknown",
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            time_s=time_s,
            channels=channel_captures,
            trigger=trigger or self._trigger,
            metadata={"driver": "pypicosdk"},
        )

    async def get_status(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            "connected": self._scope is not None,
            "device_id": self._device_id,
            "model": self._model,
            "driver_error": self._driver_error,
        }

    def _open_scope_class(self, psdk: Any) -> Any:
        candidates = [
            getattr(psdk, "ps2000", None),
            getattr(psdk, "ps2000a", None),
            getattr(psdk, "ps3000a", None),
            getattr(psdk, "ps4000a", None),
            getattr(psdk, "ps5000a", None),
            getattr(psdk, "ps6000a", None),
        ]
        for factory in candidates:
            if factory is None:
                continue
            try:
                return factory()
            except Exception:
                continue
        raise RuntimeError(
            "No compatible PicoScope class found. Ensure PicoSDK is installed and the device is connected."
        )

    def _channel_to_enum(self, psdk: Any, channel_id: str) -> Any:
        mapping = {
            "A": psdk.CHANNEL.A,
            "B": psdk.CHANNEL.B,
            "C": psdk.CHANNEL.C,
            "D": psdk.CHANNEL.D,
        }
        key = channel_id.strip().upper()
        if key not in mapping:
            raise ValueError(f"Unsupported PicoScope channel '{channel_id}'")
        return mapping[key]

    def _range_to_enum(self, psdk: Any, range_v: float) -> Any:
        choices = [
            (0.05, psdk.RANGE.V50MV),
            (0.1, psdk.RANGE.V100MV),
            (0.2, psdk.RANGE.V200MV),
            (0.5, psdk.RANGE.V500MV),
            (1.0, psdk.RANGE.V1),
            (2.0, psdk.RANGE.V2),
            (5.0, psdk.RANGE.V5),
            (10.0, psdk.RANGE.V10),
            (20.0, psdk.RANGE.V20),
        ]
        return min(choices, key=lambda item: abs(item[0] - range_v))[1]

    def _ensure_scope(self) -> None:
        if self._scope is None:
            raise RuntimeError("No PicoScope connected. Use scope_device(operation='connect').")
