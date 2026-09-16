[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Data = Join-Path ([IO.Path]::GetFullPath($PSScriptRoot)) "runtime"
$PidPath = Join-Path $Data "reference-app.pid"
if (-not (Test-Path -LiteralPath $PidPath)) {
    Write-Host "Reference app is not running."
    exit 0
}

$processId = [int](Get-Content -LiteralPath $PidPath -Raw)
$process = Get-Process -Id $processId -ErrorAction SilentlyContinue
if ($process) {
    Stop-Process -Id $processId
    Wait-Process -Id $processId -Timeout 10 -ErrorAction SilentlyContinue
    Write-Host "Stopped reference app PID $processId."
} else {
    Write-Host "Reference app process $processId was already stopped."
}
Remove-Item -LiteralPath $PidPath -Force
