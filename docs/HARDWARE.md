# Hardware Guide

USB oscilloscopes without a built-in screen are **PC-based scopes**: a small USB frontend plus software on your computer. oscilloscope-mcp replaces the vendor GUI with agent-callable tools.

## What you are buying

| Component | Role |
|-----------|------|
| USB frontend | ADC, analog front-end, BNC inputs |
| Probes | Connect to circuit under test |
| PC software | Display, decode, export (replaced by MCP) |
| SDK/driver | What oscilloscope-mcp talks to |

## Recommendations

### Tier 1 - Best value (PicoScope 2204A)

- **Price:** ~$130-190 USD
- **Specs:** 2 ch, 10 MHz, 100 MS/s, 8 kS memory, AWG included
- **Backend:** `picoscope` (pyPicoSDK + PicoSDK)
- **Why:** Official SDK, excellent Python support, same PicoScope software as expensive models
- **Good for:** MCU debug, power rails, audio, UART, I2C, SPI (moderate speed)

### Tier 2 - Swiss army knife (Digilent Analog Discovery 3)

- **Price:** ~$200-400 USD
- **Specs:** Scope + 2ch AWG + 16ch logic + programmable PSU
- **Backend:** planned (`waveforms` SDK)
- **Why:** One USB cable covers bring-up, logic, and power
- **Good for:** FPGA/MCU bring-up, lab-on-desk, pairing with kicad-mcp workflows

### Tier 3 - Budget hack (Hantek 6022BE/BL)

- **Price:** ~$40-80 USD
- **Specs:** 2 ch, ~20 MHz, 8-bit, 48 MS/s theoretical
- **Backend:** `hantek` (PyHT6022 + libusb)
- **Why:** Cheapest way to probe real hardware with open-source drivers
- **Caveats:** Noisy, dual USB on some models, 35 V max input, needs firmware flash

### USBXI (Hantek modular chassis - not your 6022BE)

**USBXI** is Hantek's proprietary **modular docking system**, not an open industry protocol like USBTMC or SCPI.

| Aspect | USBXI | USBTMC (industry standard) |
|--------|-------|------------------------------|
| What it is | Physical chassis + sync bus for stacking modules | USB device class for test equipment |
| Software | Hantek DLLs / UXI protocol | PyVISA, SCPI, vendor SDKs |
| Products | USBXI-1070A/B/C chassis + plug-in scope/PSU/LA modules | PicoScope, Siglent, Keysight, etc. |
| Budget 6022BE | Uses **normal USB** + libusb (OpenHantek/PyHT6022) | N/A on cheapest dongles |

On some Hantek 6022BL units, a port labeled USBXI allows **cascading two units** (4ch scope or 32ch logic) - still vendor-specific, not SCPI.

oscilloscope-mcp targets **USB + SDK** backends (PicoSDK, PyHT6022). A future USBXI chassis backend would need Hantek's modular SDK.

### Avoid

- Random AliExpress "USB oscilloscope" with closed Windows-only app
- Scopes with no documented API, SDK, or open-source driver
- Claims of 100 MHz at $30 - physics and ADC cost money

## Probe safety

| Signal | Safe with budget scope? |
|--------|-------------------------|
| 3.3 V / 5 V logic | Yes |
| MCU clocks (< 50 MHz) | Usually yes with decent scope |
| Mains (230 V AC) | **Never** without proper HV differential probe |
| Unknown rails | Set scope to highest range first |

Budget USB scopes typically limit input to **35-50 V** on BNC. Exceeding this damages the frontend.

## Accessories

- **10x passive probes** - include with PicoScope kits; budget ~$15-30 separately
- **Probe hook tips + ground spring** - reduce ground loop noise
- **USB 3.0 port** - dedicated port improves streaming stability

## Fleet pairing

| Your project | Suggested scope |
|--------------|-----------------|
| Arduino / ESP32 | PicoScope 2204A or simulator |
| KiCad PCB bring-up | PicoScope 2204A or Analog Discovery 3 |
| Quick logic check | Analog Discovery 3 (logic analyzer) |
| Learning / CI | Simulator only |
