# ============================================================
# ResearchOS Health & System Diagnostic Script
# ============================================================
Write-Host "Checking ResearchOS system status..." -ForegroundColor Cyan

# 1. API Health Check
try {
    $api = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 3
    Write-Host "[OK] API Server: ONLINE" -ForegroundColor Green
    Write-Host "    Operating Mode: $($api.operating_mode)" -ForegroundColor Gray
    Write-Host "    Spend Guarantee: Free Only ($($api.free_only_enforced))" -ForegroundColor Gray
    Write-Host "    Default Currency: $($api.default_currency)" -ForegroundColor Gray
    Write-Host "    Location: $($api.default_location)" -ForegroundColor Gray
} catch {
    Write-Host "[OFF] API Server: OFFLINE (Start with .\scripts\start.ps1)" -ForegroundColor Red
}

# 2. Local AI Ollama Check
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2
    $modelCount = $ollama.models.Count
    Write-Host "[OK] Local Ollama: ONLINE ($modelCount models available)" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Local Ollama: OFFLINE (Cloud free models will be used)" -ForegroundColor Yellow
}

# 3. Provider Health Check
try {
    $providers = Invoke-RestMethod -Uri "http://localhost:8000/api/providers/health" -TimeoutSec 4
    Write-Host "Provider Health Matrix:" -ForegroundColor Cyan
    foreach ($p in $providers) {
        $statusColor = if ($p.status -eq "ONLINE") { "Green" } else { "Gray" }
        Write-Host "    - $($p.name) [$($p.type)]: $($p.status)" -ForegroundColor $statusColor
    }
} catch {
    # Ignored if API is down
}
