$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Path $PSScriptRoot -Parent
Set-Location $projectRoot

python .\scripts\refresh_metrics.py *> .\scripts\refresh_metrics.log
Write-Host "Nightly refresh completed."
