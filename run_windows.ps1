$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Run setup_windows.ps1 first." -ForegroundColor Red
    exit 1
}

& .\.venv\Scripts\python.exe janitor.py
