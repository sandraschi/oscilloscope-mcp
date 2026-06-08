# Tool Catalog

All tools use the portmanteau pattern: one tool name, `operation` enum, structured JSON response.

## scope_device

Device discovery, connection, and health.

| Operation | Params | Description |
|-----------|--------|-------------|
| `list` | - | List devices from all backends |
| `connect` | `device_id`, `backend?` | Open device session |
| `disconnect` | - | Close session |
| `status` | - | Connection health + Prefab grid |
| `capabilities` | - | Bandwidth, channels, sample rate |
| `backends` | - | Available backend names |

**Examples**

```
scope_device(operation="list")
scope_device(operation="connect", device_id="sim-001")
scope_device(operation="status")
```

## scope_configure

Channel and simulator configuration.

| Operation | Params | Description |
|-----------|--------|-------------|
| `channel` | `channel_id`, `range_v`, `coupling`, `enabled` | Configure one channel |
| `get` | - | Current device info |
| `simulator_profile` | `waveform`, `frequency_hz`, `amplitude_v` | Set synthetic signal |

**Examples**

```
scope_configure(operation="channel", channel_id="A", range_v=2.0, coupling="dc")
scope_configure(operation="simulator_profile", waveform="square", frequency_hz=5000)
```

## scope_trigger

Trigger configuration.

| Operation | Params | Description |
|-----------|--------|-------------|
| `set` | `source_channel`, `threshold_v`, `mode`, `edge` | Apply trigger |
| `get` | - | Read current trigger |
| `arm` | - | Set normal mode (wait for trigger) |
| `force` | - | Software force trigger hint |

## scope_capture

Waveform acquisition and export.

| Operation | Params | Description |
|-----------|--------|-------------|
| `single` | `sample_rate_hz`, `sample_count`, `channel_id`, `range_v` | Acquire waveform |
| `preview` | - | Downsampled last capture |
| `export_csv` | `filename?` | Write CSV to capture dir |
| `export_summary` | `filename?` | Write JSON metadata + preview |
| `last` | - | Full last capture payload |

**Defaults:** 100 kHz, 2000 samples, channel A, 2 V range.

## scope_measure

Measurements from captured data.

| Operation | Params | Description |
|-----------|--------|-------------|
| `all` | `channel_id` | Vpp, freq, duty, rise, RMS |
| `vpp` | `channel_id` | Peak-to-peak only |
| `frequency` | `channel_id` | Frequency and period |
| `duty` | `channel_id` | Duty cycle percent |
| `rise_time` | `channel_id` | 10%-90% rise time |
| `fresh` | `sample_rate_hz`, `sample_count` | Capture then measure |

## scope_help

Discovery and documentation.

| Operation | Params | Description |
|-----------|--------|-------------|
| `discover` | `topic?` | List all tools |
| `tool_help` | `tool_name` | Per-tool operations |
| `status` | - | Server version and backend |
| `quickstart` | - | Step-by-step workflow |
| `faq` | `topic?` | Common questions |
| `hardware_guide` | - | Buying recommendations |

## Resources

| URI | Content |
|-----|---------|
| `resource://scope/capabilities` | Backend and tool summary |
| `resource://scope/quickstart` | Short workflow |
| `resource://scope/last_capture` | Downsampled last waveform |

## Response contract

Success:

```json
{
  "success": true,
  "operation": "single",
  "data": { }
}
```

Failure:

```json
{
  "success": false,
  "operation": "connect",
  "error": "device_id is required for connect"
}
```
