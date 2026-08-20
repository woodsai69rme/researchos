# ============================================================
# ResearchOS Windows 11 Master Launcher Script
# ============================================================
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " ResearchOS - Launching Universal Research Platform" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$baseDir = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = (Split-Path -Parent $baseDir)
Set-Location -Path $baseDir

# Check if port 8000 is already in use
$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Write-Host "[!] Port 8000 is already in use. Stopping existing instance..." -ForegroundColor Yellow
    Stop-Process -Id $portCheck.OwningProcess -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Start API Server in background process
Write-Host "[1/2] Starting ResearchOS API and Web Server on port 8000..." -ForegroundColor Yellow
$apiProcess = Start-Process python -ArgumentList "$baseDir\run_server.py" -WorkingDirectory $baseDir -PassThru -WindowStyle Hidden
Write-Host "  -> API Server started with PID: $($apiProcess.Id)" -ForegroundColor Green

# Start Periodic Monitoring Scheduler in background
Write-Host "[2/2] Starting 12h Periodic Monitoring Scheduler..." -ForegroundColor Yellow
$schedProcess = Start-Process python -ArgumentList "-m", "researchos.apps.scheduler.scheduler" -PassThru -WindowStyle Hidden
Write-Host "  -> Scheduler started with PID: $($schedProcess.Id)" -ForegroundColor Green

# Wait a brief moment and verify server response
Start-Sleep -Seconds 2
try {
    $res = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host " ResearchOS is ONLINE and OPERATIONAL!" -ForegroundColor Green
    Write-Host " Dashboard URL: http://localhost:8000" -ForegroundColor Cyan
    Write-Host " API Docs URL:  http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
} catch {
    Write-Host "Server launched. Access http://localhost:8000 in your browser." -ForegroundColor Green
}
