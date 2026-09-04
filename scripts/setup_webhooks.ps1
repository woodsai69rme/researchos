# ============================================================
# ResearchOS Webhook Configuration Wizard (Discord & Telegram)
# ============================================================
$baseDir = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $baseDir ".env"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ResearchOS Alert Notification Setup (Discord & Telegram)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $baseDir ".env.example") $envFile -Force
}

$envContent = Get-Content $envFile -Raw

Write-Host "`nEnter your notification details (or press Enter to skip):`n"

$discordUrl = Read-Host "Enter Discord Webhook URL"
if ($discordUrl.Trim()) {
    if ($envContent -match "DISCORD_WEBHOOK_URL=.*") {
        $envContent = $envContent -replace "DISCORD_WEBHOOK_URL=.*", "DISCORD_WEBHOOK_URL=$discordUrl"
    } else {
        $envContent += "`nDISCORD_WEBHOOK_URL=$discordUrl"
    }
    Write-Host "[✓] Discord Webhook saved." -ForegroundColor Green
}

$tgToken = Read-Host "Enter Telegram Bot Token"
if ($tgToken.Trim()) {
    if ($envContent -match "TELEGRAM_BOT_TOKEN=.*") {
        $envContent = $envContent -replace "TELEGRAM_BOT_TOKEN=.*", "TELEGRAM_BOT_TOKEN=$tgToken"
    } else {
        $envContent += "`nTELEGRAM_BOT_TOKEN=$tgToken"
    }
    Write-Host "[✓] Telegram Token saved." -ForegroundColor Green
}

$tgChat = Read-Host "Enter Telegram Chat ID"
if ($tgChat.Trim()) {
    if ($envContent -match "TELEGRAM_CHAT_ID=.*") {
        $envContent = $envContent -replace "TELEGRAM_CHAT_ID=.*", "TELEGRAM_CHAT_ID=$tgChat"
    } else {
        $envContent += "`nTELEGRAM_CHAT_ID=$tgChat"
    }
    Write-Host "[✓] Telegram Chat ID saved." -ForegroundColor Green
}

Set-Content -Path $envFile -Value $envContent -Encoding UTF8
Write-Host "`n[✓] Environment file updated at: $envFile" -ForegroundColor Green

Write-Host "`nTesting webhook delivery..." -ForegroundColor Cyan
python "$baseDir\packages\monitoring\test_alerts.py"
