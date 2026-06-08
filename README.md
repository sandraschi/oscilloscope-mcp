# oscilloscope-mcp

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](pyproject.toml)
[![FastMCP 3.2+](https://img.shields.io/badge/FastMCP-3.2+-green.svg)](pyproject.toml)

AI-driven USB oscilloscope control via **FastMCP 3.2**. Connect screenless PC scopes (PicoScope, Hantek) or run the built-in simulator for dry-runs. Capture waveforms, export CSV, and compute frequency, Vpp, duty cycle, and rise time from your agent.

## How it runs

| Mode | Hardware | When |
|------|----------|------|
| **Simulator (default)** | None | Development, CI, agent dry-runs |
| **PicoScope** | PicoScope 2000/3000/5000/6000 USB | Production bench with PicoSDK + pyPicoSDK |
| **Hantek** | Hantek 6022BE/BL | Budget USB scope with PyHT6022 + libusb |

The MCP server never bundles oscilloscope drivers or PicoSDK. Install vendor software separately, then point the backend at your device.

## Hands-in / Hands-out

| Direction | Artifacts | Notes |
|-----------|-----------|-------|
| **Hands-in** | `device_id`, channel config, trigger settings | Via `scope_device`, `scope_configure`, `scope_trigger` |
| **Hands-out** | Waveform preview (downsampled JSON) | `scope_capture(operation="single")` |
| **Hands-out** | CSV + JSON summary files | `scope_capture(operation="export_csv")` in `OSCILLOSCOPE_MCP_CAPTURE_DIR` |
| **Hands-out** | Measurements (Vpp, freq, duty, rise) | `scope_measure(operation="all")` |

### Fleet pipelines

| Partner MCP | Workflow |
|-------------|----------|
| [kicad-mcp](https://github.com/sandraschi/kicad-mcp) | Probe clock/reset nets after bring-up |
| [chip-design-mcp](https://github.com/sandraschi/chip-design-mcp) | Verify power rails and oscillators |
| [devices-mcp](https://github.com/sandraschi/devices-mcp) | Discover USB devices before connect |

## Quick Start

```powershell
Set-Location D:\Dev\repos\oscilloscope-mcp
uv sync --extra dev
just webapp
# Open http://localhost:10937
```

STDIO-only (Cursor MCP):

```powershell
just serve
```

Dry-run without hardware:

```
scope_device(operation="connect", device_id="sim-001")
scope_capture(operation="single", sample_rate_hz=100000, sample_count=2000)
scope_measure(operation="all", channel_id="A")
```

## Cursor MCP config

Add to `C:\Users\sandr\.cursor\mcp.json`:

```json
"oscilloscope-mcp": {
  "command": "C:/Users/sandr/.local/bin/uv.exe",
  "args": [
    "--directory",
    "D:/Dev/repos/oscilloscope-mcp",
    "run",
    "python",
    "-m",
    "oscilloscope_mcp",
    "--stdio"
  ],
  "env": {
    "FASTMCP_BANNER": "0",
    "FASTMCP_UPDATE_CHECK": "0",
    "PYTHONUNBUFFERED": "1",
    "OSCILLOSCOPE_MCP_BACKEND": "auto"
  }
}
```

## Table of Contents

- [Hardware Guide](docs/HARDWARE.md)
- [Backend Drivers](docs/BACKENDS.md)
- [Setup & Configuration](docs/SETUP.md)
- [Tool Catalog](docs/TOOLS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Safety](docs/SAFETY.md)
- [Fleet Integration](docs/FLEET_INTEGRATION.md)
- [Install (naked PC)](INSTALL.md)

## Tools Overview

| Tool | Operations | Purpose |
|------|------------|---------|
| `scope_device` | list, connect, disconnect, status, capabilities, backends | Device discovery and session |
| `scope_configure` | channel, get, simulator_profile | Voltage range, coupling, sim waveform |
| `scope_trigger` | set, get, arm, force | Trigger source, threshold, edge |
| `scope_capture` | single, preview, export_csv, export_summary, last | Acquire and export waveforms |
| `scope_measure` | all, vpp, frequency, duty, rise_time, fresh | Timing and voltage metrics |
| `scope_help` | discover, tool_help, quickstart, faq, hardware_guide | Discovery and buying guide |

## Recommended Hardware

| Tier | Model | Price | Backend |
|------|-------|-------|---------|
| Best value | PicoScope 2204A | ~$130-190 | `picoscope` |
| Swiss army knife | Analog Discovery 3 | ~$200-400 | planned (`waveforms`) |
| Budget hack | Hantek 6022BE | ~$40-80 | `hantek` |

See [docs/HARDWARE.md](docs/HARDWARE.md) for the full buying guide.

## Webapp

Fleet SOTA console: Dashboard, Waveform viewer, Tools hub, Settings, Help.

```powershell
just webapp
```

| Port | Service |
|------|---------|
| 10936 | FastAPI backend (`/api/*`, `/health`, `/mcp`) |
| 10937 | Vite React frontend |

## License

MIT - see [LICENSE](LICENSE).
