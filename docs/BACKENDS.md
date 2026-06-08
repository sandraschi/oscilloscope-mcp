# Backend Drivers

## Simulator (built-in)

Always available. No USB hardware or extra dependencies.

```powershell
scope_device(operation="connect", device_id="sim-001")
scope_configure(operation="simulator_profile", waveform="sine", frequency_hz=1000, amplitude_v=0.8)
```

Waveforms: `sine`, `square`, `ramp`, `noise`.

Use for: CI, agent dry-runs, documentation examples, development without bench.

## PicoScope

### Requirements

1. PicoScope USB device (2000/3000/5000/6000 series)
2. PicoSDK installed from https://www.picotech.com/downloads
3. Python extra:

```powershell
uv sync --extra picoscope
```

4. Environment:

```powershell
$env:OSCILLOSCOPE_MCP_BACKEND = "picoscope"
```

### Python stack

- **pyPicoSDK** - high-level Python wrapper
- **picosdk** - lower-level bindings (used for discovery)

### Connect workflow

```
scope_device(operation="list")
scope_device(operation="connect", device_id="picoscope:SERIAL")
scope_configure(operation="channel", channel_id="A", range_v=1.0)
scope_capture(operation="single", sample_rate_hz=1000000, sample_count=5000)
```

### Troubleshooting

| Issue | Resolution |
|-------|------------|
| `pyPicoSDK is not installed` | `uv sync --extra picoscope` |
| `No compatible PicoScope class` | Install PicoSDK; verify device in PicoScope app |
| Wrong voltage range | Adjust `range_v` in configure/capture |

## Hantek 6022BE/BL

### Requirements

1. Hantek 6022 or compatible (Voltcraft, Darkwire, etc.)
2. libusb + WinUSB (Windows: Zadig) or udev rules (Linux)
3. Python extra:

```powershell
uv sync --extra hantek
```

4. Custom firmware via PyHT6022 (first connect may flash)

### References

- OpenHantek6022: https://github.com/OpenHantek/OpenHantek6022
- PyHT6022 API: https://github.com/Ho-Ro/Hantek6022API

### Connect workflow

```
scope_device(operation="connect", device_id="hantek:6022", backend="hantek")
scope_capture(operation="single", sample_rate_hz=1000000, sample_count=4096)
```

### Limitations

- 8-bit resolution
- Input max ~35 V
- Some models need two USB ports for power
- `read_samples()` API may vary by firmware fork

## Auto backend selection

`OSCILLOSCOPE_MCP_BACKEND=auto` (default) tries:

1. picoscope - if devices found with `driver_status=available`
2. hantek - if devices found
3. simulator - fallback

## Planned backends

| Backend | Hardware | SDK |
|---------|----------|-----|
| waveforms | Analog Discovery 2/3 | Digilent WaveForms SDK |
| sigrok | Many USB LAs/scopes | libsigrok |
| scpi | Bench scopes (Siglent, Rigol) | PyVISA + USB/Ethernet |
