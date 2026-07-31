set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# oscilloscope-mcp project management

default:
    @just --list

version:
    @uv run python -c "import pathlib, tomllib; p = pathlib.Path('pyproject.toml'); print(tomllib.loads(p.read_text(encoding='utf-8'))['project']['version'])"

install:
    uv sync --extra dev
    uv run pre-commit install

serve:
    uv run python -m oscilloscope_mcp --stdio

serve-http:
    uv run python -m oscilloscope_mcp --http --port 10936

webapp:
    @powershell -ExecutionPolicy Bypass -File webapp/start.ps1

lint:
    uv run ruff check .
    uv run ruff format --check .

fix:
    uv run ruff check . --fix
    uv run ruff format .

test:
    uv run pytest tests/ -v -m "not integration"

test-all:
    uv run pytest tests/ -v

test-integration:
    uv run pytest tests/integration -v -m integration

ci: lint test

# Bootstrap: install dev deps + pre-commit hook
bootstrap:
    uv sync --group dev
    uv run pre-commit install
    Write-Host "Pre-commit hooks installed." -ForegroundColor Green