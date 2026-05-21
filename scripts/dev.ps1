param(
    [ValidateSet("up", "down", "logs", "status", "reset")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Path $PSScriptRoot -Parent
Set-Location $projectRoot

switch ($Action) {
    "up" {
        Write-Host "Starting stack (build + detached)..."
        docker compose up --build -d
    }
    "down" {
        Write-Host "Stopping stack..."
        docker compose down
    }
    "logs" {
        Write-Host "Showing dashboard logs..."
        docker compose logs --tail=120 dashboard
    }
    "status" {
        Write-Host "Compose service status..."
        docker compose ps
    }
    "reset" {
        Write-Host "Stopping stack and removing volumes..."
        docker compose down -v
    }
}
