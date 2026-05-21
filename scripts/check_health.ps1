param(
    [string]$Url = "http://localhost:8501",
    [int]$MaxAttempts = 30,
    [int]$SleepSeconds = 2
)

$ErrorActionPreference = "Stop"

for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "Health check passed at attempt $attempt ($Url)."
            exit 0
        }
    }
    catch {
        Write-Host "Attempt $attempt/$MaxAttempts failed. Retrying..."
    }

    if ($attempt -lt $MaxAttempts) {
        Start-Sleep -Seconds $SleepSeconds
    }
}

Write-Error "Health check failed after $MaxAttempts attempts for $Url"
exit 1
