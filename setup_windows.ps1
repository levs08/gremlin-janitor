$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python launcher 'py' was not found. Install Python 3.10+ from python.org, then rerun this script." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".venv")) {
    py -3 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env. Open it and fill DISCORD_BOT_TOKEN and TARGET_CHANNEL_ID." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists; leaving it unchanged." -ForegroundColor Green
}

Write-Host "Setup complete." -ForegroundColor Green
