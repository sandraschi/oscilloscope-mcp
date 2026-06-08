# Safety

oscilloscope-mcp controls real test equipment. Agents and operators must follow basic electrical safety.

## Input limits

| Scope class | Typical max input |
|-------------|-------------------|
| Hantek 6022 | 35 V |
| PicoScope 2204A | 50 V (varies by range) |
| Bench scopes | Check datasheet |

**Never** connect a budget USB scope directly to mains voltage.

## Safe workflows

1. Power off the circuit when attaching probes (when practical)
2. Connect ground clip to circuit ground first
3. Start with the largest voltage range, then zoom in
4. Use 10x probe for unknown signals
5. Keep fingers clear of exposed conductors

## Unsafe requests

Agents should refuse or warn when asked to:

- Probe wall outlets or mains wiring
- Measure unknown high-voltage sources without proper probes
- Bypass isolation on powered equipment

## Simulator vs hardware

The simulator backend cannot damage hardware - use it to validate agent workflows before connecting USB equipment.

## Data safety

- Captures may contain sensitive signal information
- Export files in `captures/` are not auto-deleted
- Do not commit capture CSVs to git (see `.gitignore`)

## Fleet note

For high-risk automation, pair with virtualization-mcp (Windows Sandbox) when running untrusted agent scripts alongside instrument control.
