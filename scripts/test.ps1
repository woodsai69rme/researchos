# ============================================================
# ResearchOS Automated Test Suite Runner
# ============================================================
$baseDir = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = (Split-Path -Parent $baseDir)
Set-Location -Path $baseDir

Write-Host "Running ResearchOS Unit and Integration Tests..." -ForegroundColor Cyan
python -m pytest -c pytest.ini tests/ -v
