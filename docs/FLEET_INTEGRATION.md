# Fleet Integration

oscilloscope-mcp is part of the Sandra MCP fleet (`D:/Dev/repos/`).

## Cursor registration

Server name: `oscilloscope-mcp`

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
    "PYTHONUNBUFFERED": "1"
  }
}
```

## Pipelines

### kicad-mcp bring-up

1. Export Gerber/BOM from kicad-mcp
2. Power board, identify test points
3. `scope_device(operation="connect")`
4. Probe clock crystal output: `scope_measure(operation="frequency")`
5. Verify 3.3 V rail: `scope_measure(operation="vpp")` on DC-coupled channel

### chip-design-mcp verification

1. Review power domain spec from chip-design-mcp
2. Capture rail ripple: `scope_capture(sample_rate_hz=1000000)`
3. Export evidence: `scope_capture(operation="export_csv")`

### devices-mcp discovery

Use devices-mcp to list USB devices before `scope_device(operation="list")` when debugging driver issues.

## Ports

Registered in `mcp-central-docs/operations/WEBAPP_PORTS.md`:

| Port | Service |
|------|---------|
| 10936 | oscilloscope-mcp HTTP backend |

## Standards compliance

- FastMCP 3.2+
- Portmanteau tools
- prefab-ui on list/status tools
- uv + hatchling + justfile
- llms.txt + llms-full.txt
- PowerShell-native scripts

## Future webapp

Reserved port **10937** for a Vite waveform viewer (not yet implemented). Backend would expose `GET /api/capabilities` per fleet webapp standards.
