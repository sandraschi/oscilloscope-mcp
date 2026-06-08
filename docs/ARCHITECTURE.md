# Architecture

## Overview

oscilloscope-mcp is a FastMCP 3.2+ server that exposes USB PC oscilloscopes to AI agents through portmanteau tools. The PC provides the display; the USB dongle is analog frontend + ADC.

```
Agent (Cursor/Claude)
        |
        v
  FastMCP stdio/HTTP
        |
  Portmanteau tools
  (scope_device, scope_capture, ...)
        |
  ScopeSession
        |
  Backend driver
  +-- SimulatorBackend (always)
  +-- PicoScopeBackend (optional)
  +-- HantekBackend (optional)
        |
  USB oscilloscope hardware
```

## Design principles

1. **Simulator first** - every workflow must work without hardware for CI and agent dry-runs.
2. **Portmanteau tools** - six tools instead of 30+ atomic tools; `operation` enum dispatches internally.
3. **Optional extras** - PicoScope and Hantek drivers are optional `pyproject` extras; core install stays light.
4. **Last-capture cache** - `scope_measure` and export tools read from session memory; `resource://scope/last_capture` mirrors this.
5. **Stdio safety** - all logging to stderr; Windows binary mode for stdin/stdout.

## Package layout

```
src/oscilloscope_mcp/
  app.py              # FastMCP instance, lifespan, resources
  server.py           # Entry point
  transport.py        # stdio / HTTP / SSE
  config.py           # pydantic-settings
  models/             # Pydantic v2 capture/device models
  services/
    session.py        # Backend selection and connection
    registry.py       # Global session + last capture
    backends/         # Driver implementations
  tools/portmanteau/  # MCP tools
  utils/              # measurements, export, logging
```

## Lifespan hook

On startup:

1. Load settings from environment
2. Resolve backend (`auto` tries picoscope, hantek, then simulator)
3. Probe device list (shallow connectivity check)
4. Ensure capture directory exists

On shutdown:

1. Disconnect active backend
2. Clear session and last capture

## Backend interface

Every backend implements `OscilloscopeBackend`:

- `list_devices()` - discovery
- `connect(device_id)` - open session
- `configure_channels()` / `configure_trigger()`
- `capture_block()` - single acquisition
- `get_status()` - health

## Capture pipeline

1. Agent calls `scope_capture(operation="single", ...)`
2. Tool ensures backend is connected
3. Backend acquires samples + time axis
4. `WaveformCapture` stored in registry
5. Downsampled preview returned to agent
6. Full data available via `export_csv` or `resource://scope/last_capture`

## Measurement pipeline

1. Read last capture (or fresh capture via `scope_measure(operation="fresh")`)
2. Select channel by `channel_id`
3. `compute_measurements()` derives Vpp, frequency, duty, rise time
4. Edge detection uses threshold crossing with linear interpolation

## Future backends

| Backend | SDK | Status |
|---------|-----|--------|
| WaveForms (Analog Discovery) | FDwf Python ctypes | planned |
| sigrok | libsigrok CLI / Python | planned |
| SCPI (bench scopes) | PyVISA | planned |

## Ports

- **10936** - HTTP MCP transport (fleet registry)
