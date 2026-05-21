# Demo Day Release Checklist

## 1. Environment Readiness
- [ ] Docker Desktop running on demo machine
- [ ] Required ports available: 8501 (dashboard), 5432 (PostgreSQL)
- [ ] Latest code pulled from default branch

## 2. Stack Bring-up
- [ ] Run: `powershell -ExecutionPolicy Bypass -File .\\scripts\\dev.ps1 -Action up`
- [ ] Verify services: `docker compose ps`
- [ ] Confirm `postgres` status is healthy
- [ ] Confirm dashboard reachable at http://localhost:8501

## 3. Data and KPI Validation
- [ ] Trigger data refresh from dashboard sidebar or run `python .\\run_etl.py`
- [ ] Validate KPI cards render with non-zero values
- [ ] Validate filter behavior (warehouse, customer, date range)
- [ ] Validate charts update correctly with filters

## 4. Reporting Validation
- [ ] Export filtered shipments CSV from dashboard
- [ ] Export Excel KPI+shipment report from dashboard
- [ ] Run CLI report pack: `python .\\scripts\\export_weekly_report.py`
- [ ] Confirm files exist in `reports/generated/`

## 5. Reliability Checks
- [ ] Health check passes: `powershell -ExecutionPolicy Bypass -File .\\scripts\\check_health.ps1 -Url "http://localhost:8501"`
- [ ] No critical errors in dashboard logs: `docker compose logs --tail=200 dashboard`

## 6. Demo Flow Dry Run
- [ ] 2-minute architecture walkthrough
- [ ] 3-minute dashboard walkthrough (filters + trends)
- [ ] 2-minute reporting/export walkthrough
- [ ] 1-minute automation/CI mention

## 7. Rollback/Recovery Preparedness
- [ ] Know stack stop command: `powershell -ExecutionPolicy Bypass -File .\\scripts\\dev.ps1 -Action down`
- [ ] Know full reset command: `powershell -ExecutionPolicy Bypass -File .\\scripts\\dev.ps1 -Action reset`
- [ ] Have a backup branch/tag available for fallback
