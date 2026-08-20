# ============================================================
# ResearchOS Database & Full Codebase Backup Script
# Backs up locally and mirrors directly to X: drive
# ============================================================
$baseDir = Split-Path -Parent $PSScriptRoot
$dataDir = Join-Path $baseDir 'data'
$localBackupDir = Join-Path $baseDir 'backups'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

New-Item -ItemType Directory -Force -Path $localBackupDir | Out-Null

# 1. Local Database Backup
$dbFile = Join-Path $dataDir 'researchos.db'
if (Test-Path $dbFile) {
    $targetBackup = Join-Path $localBackupDir "researchos_backup_$timestamp.db"
    Copy-Item -Path $dbFile -Destination $targetBackup -Force
    Write-Host '[OK] Local DB backup created at: ' $targetBackup -ForegroundColor Green
}

# 2. X: Drive Mirrors and Snapshots (if drive X: is mounted)
if (Test-Path 'X:\') {
    Write-Host '[*] Syncing ResearchOS codebase to X: drive...' -ForegroundColor Cyan
    $xDirect = 'X:\researchos'
    $xBackup = "X:\Development_Backups\researchos_backup_$timestamp"

    New-Item -ItemType Directory -Force -Path $xDirect | Out-Null
    New-Item -ItemType Directory -Force -Path $xBackup | Out-Null

    robocopy $baseDir $xDirect /MIR /XD __pycache__ .pytest_cache node_modules .next /R:1 /W:1 /XF *.db | Out-Null
    robocopy $baseDir $xBackup /MIR /XD __pycache__ .pytest_cache node_modules .next /R:1 /W:1 /XF *.db | Out-Null

    Write-Host '[OK] Mirrored to: ' $xDirect -ForegroundColor Green
    Write-Host '[OK] Snapshot to: ' $xBackup -ForegroundColor Green
} else {
    Write-Host '[INFO] Drive X: not detected; skipping external drive backup.' -ForegroundColor Yellow
}
