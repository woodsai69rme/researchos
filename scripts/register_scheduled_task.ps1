# Windows 11 Task Scheduler Registration Script
$taskName = 'ResearchOS_Autonomous_Monitor'
$baseDir = Split-Path -Parent $PSScriptRoot
$pythonExe = 'C:\Program Files\Python313\python.exe'
$actionScript = Join-Path $baseDir 'run_server.py'

Write-Host 'Registering Windows Scheduled Task: ' $taskName -ForegroundColor Cyan

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument $actionScript -WorkingDirectory $baseDir
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description 'ResearchOS Universal Search and 12-hour Monitoring Service' | Out-Null
    Write-Host '[OK] Task registered successfully in Windows Task Scheduler!' -ForegroundColor Green
} catch {
    Write-Host '[INFO] Task registration requires elevated permissions; service can be launched via START_RESEARCHOS.bat' -ForegroundColor Yellow
}
