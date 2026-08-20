# ============================================================
# ResearchOS Catalog & Dependency Update Script
# ============================================================
$baseDir = Split-Path -Parent $PSScriptRoot
Set-Location -Path $baseDir

Write-Host "Updating ResearchOS dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt --upgrade
Write-Host "[✓] ResearchOS dependencies up to date." -ForegroundColor Green
