# Lance ngrok vers le backend local (port 8000)
$ngrok = Join-Path $PSScriptRoot "..\tools\ngrok\ngrok.exe"
if (-not (Test-Path $ngrok)) {
    Write-Host "ngrok introuvable. Telechargez-le dans tools/ngrok/ ou executez l'installation depuis SETUP_LOCAL.md"
    exit 1
}
Write-Host "Tunnel public -> http://127.0.0.1:8000"
Write-Host "Webhook Meta: https://VOTRE-URL.ngrok-free.app/api/v1/whatsapp/webhook/"
Write-Host ""
& $ngrok http 8000
