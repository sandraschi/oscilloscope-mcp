set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

# oscilloscope-mcp project management

default:
    @just --list

version:
    @uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

install:
    uv sync --extra dev
    pre-commit install

serve:
    uv run python -m oscilloscope_mcp --stdio

serve-http:
    uv run python -m oscilloscope_mcp --http --port 10936

webapp:
    @powershell -ExecutionPolicy Bypass -File webapp/start.ps1

lint:
    ruff check .
    ruff format --check .

fix:
    ruff check . --fix
    ruff format .

test:
    uv run pytest tests/ -v -m "not integration"

test-all:
    uv run pytest tests/ -v

test-integration:
    uv run pytest tests/integration -v -m integration

mcpb-pack:
    $ver = (Get-Content pyproject.toml | Select-String '^version = "(.*)"' | ForEach-Object { $_.Matches.Groups[1].Value })
    $null = New-Item -ItemType Directory -Path dist -Force
    npx --yes @anthropic-ai/mcpb@latest validate .
    npx --yes @anthropic-ai/mcpb@latest pack . "dist/oscilloscope-mcp-v$ver.mcpb"
    Write-Host "Created dist/oscilloscope-mcp-v$ver.mcpb" -ForegroundColor Green

ci: lint test
