# Demarre PostgreSQL + Redis (Docker) et prepare la base WhatBot Pro
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== WhatBot Pro - PostgreSQL + Redis ===" -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR: Docker Desktop n'est pas installe ou pas demarre." -ForegroundColor Red
    Write-Host "Installez Docker: https://www.docker.com/products/docker-desktop/"
    exit 1
}

Write-Host "Demarrage des conteneurs (postgres:5433, redis:6380)..."
docker compose -f docker-compose.postgres.yml up -d

Write-Host "Attente PostgreSQL..."
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    $status = docker inspect -f "{{.State.Health.Status}}" whatbot_postgres 2>$null
    if ($status -eq "healthy") {
        $ready = $true
        break
    }
    Start-Sleep -Seconds 2
}
if (-not $ready) {
    Write-Host "ATTENTION: Postgres pas encore healthy - verifiez: docker compose -f docker-compose.postgres.yml logs db" -ForegroundColor Yellow
} else {
    Write-Host "PostgreSQL OK" -ForegroundColor Green
}

Write-Host "Extension pgvector..."
docker exec whatbot_postgres psql -U whatbot -d whatbot_pro -c "CREATE EXTENSION IF NOT EXISTS vector;" | Out-Null

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creation du venv..."
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
}

$env:DJANGO_SETTINGS_MODULE = "whatbot_pro.settings.postgres_local"
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $idx = $line.IndexOf("=")
            $key = $line.Substring(0, $idx).Trim()
            $val = $line.Substring($idx + 1).Trim()
            [System.Environment]::SetEnvironmentVariable($key, $val)
        }
    }
}

Write-Host "Migrations..."
.\.venv\Scripts\python manage.py migrate --noinput

Write-Host "Seed demo (si besoin)..."
.\.venv\Scripts\python manage.py seed_data

Write-Host ""
Write-Host "Pret. Lancez l'API avec: .\scripts\dev.ps1" -ForegroundColor Green
Write-Host "  Postgres: localhost:5433 / db=whatbot_pro / user=whatbot / pass=whatbot"
Write-Host "  Redis:    localhost:6380"
Write-Host "  Arreter:  docker compose -f docker-compose.postgres.yml down"
