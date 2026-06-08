# oscilloscope-mcp - Install Guide

Naked-PC install standard for Windows. Assumes PowerShell and winget.

## Option A - Cursor MCP (recommended)

1. Clone or copy repo to `D:\Dev\repos\oscilloscope-mcp`
2. Install [uv](https://docs.astral.sh/uv/): `winget install astral-sh.uv`
3. Sync dependencies:

```powershell
Set-Location D:\Dev\repos\oscilloscope-mcp
uv sync --extra dev
```

4. Add MCP entry to `C:\Users\sandr\.cursor\mcp.json` (see [README.md](README.md#cursor-mcp-config))
5. Restart Cursor
6. Verify: `scope_help(operation="status")`

## Option A2 - Claude Desktop MCPB

1. Build or download `oscilloscope-mcp-v0.1.0.mcpb` from [Releases](https://github.com/sandraschi/oscilloscope-mcp/releases)
2. Or build locally:

```powershell
Set-Location D:\Dev\repos\oscilloscope-mcp
npx --yes @anthropic-ai/mcpb@latest validate .
npx --yes @anthropic-ai/mcpb@latest pack . dist/oscilloscope-mcp-v0.1.0.mcpb
```

3. Drag the `.mcpb` file into Claude Desktop
4. Requires [uv](https://docs.astral.sh/uv/) on PATH for the bundled server

## Option B - HTTP mode (remote agents)

```powershell
uv sync --extra dev
uv run python -m oscilloscope_mcp --http --port 10936
```

Health check: `http://127.0.0.1:10936/health`

## Option C - With PicoScope hardware

1. Complete Option A
2. Install PicoSDK from https://www.picotech.com/downloads
3. Install Python extra:

```powershell
uv sync --extra picoscope
```

4. Set backend:

```powershell
$env:OSCILLOSCOPE_MCP_BACKEND = "picoscope"
```

5. Connect USB PicoScope, then: `scope_device(operation="list")`

## Option D - With Hantek 6022

1. Complete Option A
2. Install libusb and WinUSB driver (Zadig on Windows)
3. Install Python extra:

```powershell
uv sync --extra hantek
```

4. See [docs/BACKENDS.md](docs/BACKENDS.md#hantek-6022bebl) for firmware notes

## Simulator-only (no hardware)

No extra steps. Default backend falls back to simulator:

```
scope_device(operation="connect", device_id="sim-001")
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `pyPicoSDK is not installed` | `uv sync --extra picoscope` + install PicoSDK |
| No devices in list | Check USB cable, driver, `scope_device(operation="backends")` |
| Stdio hangs | Ensure logging goes to stderr only; set `OSCILLOSCOPE_ALLOW_LOGGING=1` for debug |
| Import errors | `uv sync --extra dev` from repo root |

## Anti-patterns

- Do not commit `.env` with device serials
- Do not probe mains or unknown high voltage without proper probes
- Do not use Linux-only shell syntax in PowerShell scripts
