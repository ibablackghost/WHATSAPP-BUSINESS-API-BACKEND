# Lance WhatBot Pro (PostgreSQL + Redis via Docker)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creation du venv..."
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

$env:DJANGO_SETTINGS_MODULE = "whatbot_pro.settings.postgres_local"
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

# Verifier que Postgres Docker tourne
$pgRunning = docker ps --filter "name=whatbot_postgres" --filter "status=running" -q 2>$null
if (-not $pgRunning) {
    Write-Host "PostgreSQL non demarre. Lancez d'abord: .\scripts\postgres.ps1" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "API: http://127.0.0.1:8000/api/docs/"
Write-Host "Compte: admin@whatbot.pro / Admin@WhatBot2024!"
Write-Host "Webhook Meta: URL HTTPS Railway (voir RAILWAY-DEPLOY.md) — ngrok non utilise"
Write-Host ""
.\.venv\Scripts\python manage.py runserver
