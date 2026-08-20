# ============================================================
# ResearchOS Windows 11 Process Stopper
# ============================================================
Write-Host "Stopping ResearchOS services..." -ForegroundColor Yellow

$portCheck = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portCheck) {
    Stop-Process -Id $portCheck.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  -> Stopped ResearchOS API & Web server on port 8000." -ForegroundColor Green
} else {
    Write-Host "  -> No active server found on port 8000." -ForegroundColor Gray
}

# Stop background scheduler if running
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*researchos.apps.scheduler*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "ResearchOS services stopped." -ForegroundColor Green
