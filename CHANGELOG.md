# Changelog

## 0.1.0 - 2026-06-08

### Added

- FastMCP 3.2+ server with six portmanteau tools
- Simulator backend (always available)
- PicoScope backend (optional `picoscope` extra)
- Hantek 6022 backend (optional `hantek` extra)
- Waveform capture, CSV/JSON export, measurements (Vpp, freq, duty, rise)
- Resources: capabilities, quickstart, last_capture
- Fleet webapp on ports 10936/10937 (waveform viewer)
- Fleet documentation: PRD, HARDWARE, BACKENDS, SAFETY, FLEET_INTEGRATION
- Discovery: `llms.txt`, `llms-full.txt`, `glama.json`
- MCPB package: `manifest.json`, `just mcpb-pack` → `dist/oscilloscope-mcp-v0.1.0.mcpb`
- CI workflow (Windows, ruff, pytest)
