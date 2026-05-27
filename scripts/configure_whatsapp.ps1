# Configure WhatsApp credentials for Demo Organization
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "1) Login..."
$login = Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/login/" `
  -ContentType "application/json" `
  -Body '{"email":"admin@whatbot.pro","password":"Admin@WhatBot2024!"}'

$access = $login.tokens.access
Write-Host "   Token OK"

Write-Host "2) Config WhatsApp..."
if (-not $env:WABA_ID) { $env:WABA_ID = Read-Host "WhatsApp Business Account ID (WABA)" }
if (-not $env:META_TOKEN) { $env:META_TOKEN = Read-Host "Meta access token" }
$phoneId = if ($env:PHONE_NUMBER_ID) { $env:PHONE_NUMBER_ID } else { "1146571278536688" }

$result = Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/organizations/whatsapp-config/" `
  -Headers @{ Authorization = "Bearer $access" } `
  -ContentType "application/json" `
  -Body (@{
    phone_number_id = $phoneId
    business_account_id = $env:WABA_ID
    access_token = $env:META_TOKEN
  } | ConvertTo-Json)

Write-Host "3) Resultat:" ($result | ConvertTo-Json)
Write-Host "OK - WhatsApp configure pour l'organisation demo"
