# Setup and Configuration

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OSCILLOSCOPE_MCP_BACKEND` | `auto` | `auto`, `simulator`, `picoscope`, `hantek` |
| `OSCILLOSCOPE_MCP_DEVICE_ID` | - | Preferred device serial/ID |
| `OSCILLOSCOPE_MCP_CAPTURE_DIR` | `./captures` | CSV/JSON export directory |
| `OSCILLOSCOPE_MCP_TRANSPORT` | `stdio` | `stdio`, `http`, `sse` |
| `OSCILLOSCOPE_MCP_HOST` | `127.0.0.1` | HTTP bind address |
| `OSCILLOSCOPE_MCP_PORT` | `10936` | HTTP port |
| `OSCILLOSCOPE_MCP_PATH` | `/mcp` | HTTP MCP path |
| `OSCILLOSCOPE_MCP_LOG_LEVEL` | `INFO` | Log level (stderr only) |
| `OSCILLOSCOPE_ALLOW_LOGGING` | `0` | Set `1` to enable logging in stdio mode |

Copy `.env.example` to `.env` for local overrides.

## Install steps

```powershell
Set-Location D:\Dev\repos\oscilloscope-mcp
uv sync --extra dev
```

### With PicoScope

```powershell
uv sync --extra picoscope
# Install PicoSDK from picotech.com
```

### With Hantek

```powershell
uv sync --extra hantek
# Configure libusb / WinUSB per docs/BACKENDS.md
```

## Run modes

### STDIO (Cursor default)

```powershell
uv run python -m oscilloscope_mcp --stdio
```

### HTTP

```powershell
uv run python -m oscilloscope_mcp --http --port 10936
```

Health: `http://127.0.0.1:10936/health`

## First capture checklist

1. `scope_help(operation="quickstart")`
2. `scope_device(operation="list")`
3. `scope_device(operation="connect", device_id="sim-001")`
4. `scope_configure(operation="channel", channel_id="A", range_v=2.0)`
5. `scope_trigger(operation="set", source_channel="A", threshold_v=0.0, mode="auto")`
6. `scope_capture(operation="single")`
7. `scope_measure(operation="all")`

## Capture directory

Exports land in `OSCILLOSCOPE_MCP_CAPTURE_DIR`:

```
captures/
  capture_20260608_143022.csv
  capture_20260608_143022.json
```

CSV format: `time_s`, `A_v`, `B_v`, ...

## Development

```powershell
just install
just lint
just test
just serve
```
