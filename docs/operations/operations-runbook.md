# Logistix Dashboard - Operations Runbook

## Purpose
This runbook provides day-to-day operating steps for the logistics analytics stack, including startup, health checks, report generation, and troubleshooting.

## Service Endpoints
- Dashboard: http://localhost:8501
- PostgreSQL: localhost:5432

## Standard Operating Procedures

### 1) Start Platform
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action up
```

### 2) Validate Health
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_health.ps1 -Url "http://localhost:8501"
```

### 3) Confirm Container State
```powershell
docker compose ps
```

### 4) View Application Logs
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action logs
```

### 5) Generate Weekly Customer Report Pack
```powershell
python .\scripts\export_weekly_report.py
```
Output artifacts are written to `reports/generated/`.

### 6) Stop Platform
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action down
```

## Failure Playbook

### Dashboard unavailable
1. Check status:
```powershell
docker compose ps
```
2. Review app logs:
```powershell
docker compose logs --tail=200 dashboard
```
3. Restart service:
```powershell
docker compose restart dashboard
```

### Database connectivity errors
1. Verify DB health:
```powershell
docker compose ps
```
2. Confirm `postgres` is healthy and port 5432 is bound.
3. If corrupted state suspected, reset stack volume:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action reset
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action up
```

### Data appears stale
1. Trigger source reload from dashboard button or run ETL directly:
```powershell
python .\run_etl.py
```
2. Refresh dashboard page and re-run health check.

## Change Management
- Use pull requests for script/config changes.
- Require successful workflow: `.github/workflows/docker-healthcheck.yml`.
- Attach generated weekly report artifacts for stakeholder review when releasing KPI changes.
