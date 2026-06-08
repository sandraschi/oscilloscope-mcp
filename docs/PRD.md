# Product Requirements Document — Oscilloscope MCP

**Version:** 0.1.0  
**Last updated:** 2026-06-08  
**Repo:** https://github.com/sandraschi/oscilloscope-mcp  
**Fleet pair:** [logic-analyzer-mcp](https://github.com/sandraschi/logic-analyzer-mcp) (digital buses)

---

## Overview

Oscilloscope MCP is a **FastMCP 3.2+** server plus React webapp that lets AI agents and humans control **USB PC oscilloscopes** (screenless frontends). The host PC is the display; the USB device is analog frontend + ADC. Simulator backend enables CI and agent dry-runs without hardware.

## Problem statement

- USB scopes are cheap but lack SDK-unified agent interfaces.
- Agents need honest capture/export contracts, not fake waveforms.
- Fleet bench workflows pair analog scope with logic analyzer and KiCad bring-up.

## Target audience

| Persona | Need |
|---------|------|
| Agent / IDE user | Portmanteau tools, dry-run simulator, CSV export |
| Bench tinkerer | PicoScope or Hantek 6022BE via optional extras |
| Fleet operator | stdio MCP, HTTP :10936, webapp :10937, MCPB package |

## Success metrics

| Metric | Target |
|--------|--------|
| Simulator dry-run | Connect `sim-001` → capture → measure in &lt;5 tool calls |
| Stdio safety | No stdout logging in default MCP mode |
| Honesty | Missing PicoSDK/Hantek driver returns actionable error |
| Discovery | `llms.txt`, `glama.json`, `GET /api/capabilities` |

## Functional requirements

### MCP tools (portmanteau)

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-TOOL-01 | `scope_device` — list, connect, disconnect, status, backends | Done |
| REQ-TOOL-02 | `scope_configure` — channel, coupling, range, simulator profile | Done |
| REQ-TOOL-03 | `scope_trigger` — set, get, arm, force | Done |
| REQ-TOOL-04 | `scope_capture` — single, preview, export_csv, export_summary | Done |
| REQ-TOOL-05 | `scope_measure` — Vpp, frequency, duty, rise time | Done |
| REQ-TOOL-06 | `scope_help` — discover, quickstart, hardware_guide, faq | Done |

### Backends

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-BE-01 | Simulator always available | Done |
| REQ-BE-02 | PicoScope via pyPicoSDK + PicoSDK (optional extra) | Done |
| REQ-BE-03 | Hantek 6022 via PyHT6022 (optional extra) | Done |

### Webapp

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-WEB-01 | Dashboard, waveform viewer, tools hub | Done |
| REQ-WEB-02 | Vite proxy `/api` → backend :10936 | Done |
| REQ-WEB-03 | `just webapp` PowerShell launcher | Done |

### Distribution

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-DIST-01 | `manifest.json` + `.mcpb` Claude Desktop bundle | Done |
| REQ-DIST-02 | `glama.json` fleet discovery | Done |
| REQ-DIST-03 | `llms.txt` agent index | Done |

## Non-functional requirements

| Area | Requirement |
|------|-------------|
| Safety | Document low-voltage limits; never probe mains without HV probes |
| Performance | Preview downsampling for large captures |
| Portability | Windows-first; stdio + HTTP transport |

## Out of scope (v0.1)

- Analog Discovery 3 WaveForms backend (planned)
- Built-in PicoSDK or libusb redistribution
- Continuous streaming / deep memory modes

## Fleet pipelines

| Partner | Workflow |
|---------|----------|
| logic-analyzer-mcp | Mixed-signal MCU/FPGA debug |
| kicad-mcp | Post-layout rail and clock verification |
| chip-design-mcp | Power rail and oscillator checks |
