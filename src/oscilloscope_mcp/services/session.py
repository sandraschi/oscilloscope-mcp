"""Scope session orchestration across backends."""

from __future__ import annotations

from oscilloscope_mcp.config import BackendPreference, get_settings
from oscilloscope_mcp.models.device import DeviceInfo
from oscilloscope_mcp.services.backends.base import OscilloscopeBackend
from oscilloscope_mcp.services.backends.hantek import HantekBackend
from oscilloscope_mcp.services.backends.picoscope import PicoScopeBackend
from oscilloscope_mcp.services.backends.simulator import SimulatorBackend


class ScopeSession:
    """Manages backend selection, connection, and preference resolution."""

    def __init__(self) -> None:
        self._backend: OscilloscopeBackend | None = None
        self._backend_name: str | None = None
        self._available_backends: dict[str, OscilloscopeBackend] = {
            "simulator": SimulatorBackend(),
            "picoscope": PicoScopeBackend(),
            "hantek": HantekBackend(),
        }

    @property
    def backend(self) -> OscilloscopeBackend | None:
        return self._backend

    @property
    def backend_name(self) -> str | None:
        return self._backend_name

    def list_backend_names(self) -> list[str]:
        return list(self._available_backends.keys())

    def get_backend(self, name: str) -> OscilloscopeBackend:
        backend = self._available_backends.get(name)
        if backend is None:
            raise ValueError(f"Unknown backend '{name}'. Available: {', '.join(self.list_backend_names())}")
        return backend

    async def resolve_backend(self, preference: BackendPreference | None = None) -> OscilloscopeBackend:
        """Pick backend from settings or explicit preference."""
        pref = preference or get_settings().backend
        if pref != "auto":
            backend = self.get_backend(pref)
            self._backend = backend
            self._backend_name = pref
            return backend

        for name in ("picoscope", "hantek", "simulator"):
            backend = self.get_backend(name)
            try:
                devices = await backend.list_devices()
                if any(d.driver_status == "available" for d in devices):
                    self._backend = backend
                    self._backend_name = name
                    return backend
            except Exception:
                continue

        backend = self.get_backend("simulator")
        self._backend = backend
        self._backend_name = "simulator"
        return backend

    async def list_all_devices(self) -> list[DeviceInfo]:
        """Enumerate devices from every backend."""
        from oscilloscope_mcp.models.device import DeviceCapabilities

        devices: list[DeviceInfo] = []
        for name in self.list_backend_names():
            backend = self.get_backend(name)
            try:
                found = await backend.list_devices()
                devices.extend(found)
            except Exception as exc:
                devices.append(
                    DeviceInfo(
                        device_id=f"{name}:unavailable",
                        backend=name,  # type: ignore[arg-type]
                        model=f"{name} backend",
                        connected=False,
                        capabilities=DeviceCapabilities(
                            backend="simulator",
                            channels=1,
                            max_sample_rate_hz=1,
                            notes=f"Backend unavailable: {exc}",
                        ),
                        driver_status="unavailable",
                        driver_hint=str(exc),
                    )
                )
        return devices

    async def connect(self, device_id: str, *, backend: str | None = None) -> DeviceInfo:
        """Connect to a device by ID, optionally forcing backend."""
        if backend:
            selected = self.get_backend(backend)
        else:
            backend_prefix = device_id.split(":", maxsplit=1)[0]
            if backend_prefix in self._available_backends:
                selected = self.get_backend(backend_prefix)
            else:
                selected = await self.resolve_backend()

        if self._backend and self._backend is not selected:
            await self._backend.disconnect()

        self._backend = selected
        self._backend_name = selected.name
        return await selected.connect(device_id)

    async def disconnect(self) -> None:
        if self._backend is not None:
            await self._backend.disconnect()
        self._backend = None
        self._backend_name = None
