# ============================================================
# ResearchOS Database & Watchlist Backup Script
# ============================================================
$baseDir = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $baseDir "data"
$backupDir = Join-Path $baseDir "backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$dbFile = Join-Path $dataDir "researchos.db"
if (Test-Path $dbFile) {
    $targetBackup = Join-Path $backupDir "researchos_backup_$timestamp.db"
    Copy-Item -Path $dbFile -Destination $targetBackup
    Write-Host "[✓] Database backup created at: $targetBackup" -ForegroundColor Green
} else {
    Write-Host "[!] No database file found in data directory to backup." -ForegroundColor Yellow
}
