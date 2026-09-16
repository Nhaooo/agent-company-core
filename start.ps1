[CmdletBinding()]
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"
$Root = [IO.Path]::GetFullPath($PSScriptRoot)
$Data = Join-Path $Root "runtime"
$PidPath = Join-Path $Data "reference-app.pid"
$OutputLog = Join-Path $Data "reference-app.out.log"
$ErrorLog = Join-Path $Data "reference-app.err.log"
$python = (Get-Command python -ErrorAction Stop).Source

New-Item -ItemType Directory -Force -Path $Data | Out-Null
if (Test-Path -LiteralPath $PidPath) {
    $existingPid = [int](Get-Content -LiteralPath $PidPath -Raw)
    if (Get-Process -Id $existingPid -ErrorAction SilentlyContinue) {
        Write-Host "Reference app already running with PID $existingPid on http://127.0.0.1:$Port"
        exit 0
    }
    Remove-Item -LiteralPath $PidPath -Force
}

$env:PYTHONPATH = Join-Path $Root "src"
$process = Start-Process -FilePath $python -ArgumentList @(
    "-m", "uvicorn", "agent_company_core.reference.app:app",
    "--host", "127.0.0.1", "--port", $Port
) -WorkingDirectory $Root -RedirectStandardOutput $OutputLog -RedirectStandardError $ErrorLog -PassThru -WindowStyle Hidden
$process.Id | Set-Content -LiteralPath $PidPath -Encoding utf8
Write-Host "Reference app started with PID $($process.Id): http://127.0.0.1:$Port"
