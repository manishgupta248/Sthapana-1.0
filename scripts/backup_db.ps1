# scripts/backup_db.ps1
#
# Copies the SQLite database into backups/ with a timestamp, then
# deletes any backup copies older than $RetentionDays.
#
# Run manually for now: right-click this file > "Run with PowerShell",
# or run ".\scripts\backup_db.ps1" from the project root.

$RetentionDays = 30

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DbPath = Join-Path $ProjectRoot "db.sqlite3"
$BackupDir = Join-Path $ProjectRoot "backups"

if (-not (Test-Path $DbPath)) {
    Write-Host "ERROR: Database file not found at $DbPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupFile = Join-Path $BackupDir "db_$Timestamp.sqlite3"

Copy-Item -Path $DbPath -Destination $BackupFile
Write-Host "Backup created: $BackupFile" -ForegroundColor Green

# Prune old backups
$CutoffDate = (Get-Date).AddDays(-$RetentionDays)
$OldBackups = Get-ChildItem -Path $BackupDir -Filter "db_*.sqlite3" |
    Where-Object { $_.LastWriteTime -lt $CutoffDate }

foreach ($old in $OldBackups) {
    Remove-Item $old.FullName
    Write-Host "Deleted old backup: $($old.Name)" -ForegroundColor Yellow
}

Write-Host "Backup complete. $(($OldBackups | Measure-Object).Count) old backup(s) removed."