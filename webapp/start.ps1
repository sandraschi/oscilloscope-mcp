param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$WebRoot = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $WebRoot
$BackendPort = 10936
$FrontendPort = 10937

Write-Host "=== oscilloscope-mcp webapp launcher ===" -ForegroundColor Cyan

foreach ($port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.OwningProcess -gt 4) {
            Write-Host "Killing stale process $($_.OwningProcess) on port $port" -ForegroundColor Yellow
            Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
}

if (-not $FrontendOnly) {
    Write-Host "Starting backend on port $BackendPort..." -ForegroundColor Green
    $backendCmd = "Set-Location '$ProjectRoot'; uv run uvicorn oscilloscope_mcp.server:app --host 127.0.0.1 --port $BackendPort --log-level warning"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $ProjectRoot

    $ready = $false
    for ($i = 0; $i -lt 90; $i++) {
        try {
            $c = [System.Net.Sockets.TcpClient]::new()
            $c.Connect("127.0.0.1", $BackendPort)
            $c.Close()
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ready) {
        Write-Host "Backend did not listen on $BackendPort within 90s" -ForegroundColor Red
        exit 1
    }
    Write-Host "Backend ready." -ForegroundColor Green
}

if (-not $BackendOnly) {
    Set-Location $WebRoot
    if (-not (Test-Path "node_modules")) { npm install }
    Write-Host "Starting Vite on port $FrontendPort..." -ForegroundColor Green
    if (-not $NoBrowser) {
        $url = "http://127.0.0.1:$FrontendPort/"
        $poll = "for (`$i=0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$url' -TimeoutSec 2 -UseBasicParsing; Start-Process '$url'; break } catch { Start-Sleep 1 } }"
        Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $poll
    }
    npm run dev -- --port $FrontendPort --host 127.0.0.1 --strictPort
}
