# Lance WhatBot Pro en mode local (sans Docker)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creation du venv..."
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

$env:DJANGO_SETTINGS_MODULE = "whatbot_pro.settings.local"
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

Write-Host "Migrations..."
.\.venv\Scripts\python manage.py migrate --noinput

if (-not (Test-Path "db.sqlite3")) {
    Write-Host "Seed des donnees demo..."
    .\.venv\Scripts\python manage.py seed_data
}

Write-Host ""
Write-Host "API: http://127.0.0.1:8000/api/docs/"
Write-Host "Admin: admin@whatbot.pro / Admin@WhatBot2024!"
Write-Host ""
.\.venv\Scripts\python manage.py runserver
