# Contributing

## Setup

```powershell
Set-Location D:\Dev\repos\oscilloscope-mcp
uv sync --extra dev
just install
```

## Quality gates

```powershell
just lint
just test
just ci
```

## Conventions

- FastMCP 3.2+ portmanteau tools with `operation` enums
- Pydantic v2 models (`.model_dump()`, not `.dict()`)
- PowerShell-native scripts (no `&&`, no Linux-only syntax)
- Logging to stderr only in stdio mode
- Conventional commits: `feat:`, `fix:`, `docs:`

## Adding a backend

1. Implement `OscilloscopeBackend` in `src/oscilloscope_mcp/services/backends/`
2. Register in `ScopeSession._available_backends`
3. Document in `docs/BACKENDS.md`
4. Add optional extra in `pyproject.toml`
5. Add tests (simulator pattern or hardware-marked integration test)

## Hardware tests

Mark real USB tests with `@pytest.mark.hardware` and `@pytest.mark.integration`.
