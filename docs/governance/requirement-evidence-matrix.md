# Requirement to Evidence Matrix

## Summary
All requested requirements have been implemented and validated in the current workspace.

## Matrix

| Requirement | Status | Implementation Evidence | Validation Evidence |
|---|---|---|---|
| Provide simulated warehouse data in CSV/JSON | Complete | [data/shipments.json](../data/shipments.json), [data/inventory.csv](../data/inventory.csv) | Data loaded by ETL into SQL via [run_etl.py](../run_etl.py) |
| Parse and load data into SQL (SQL Server or PostgreSQL) | Complete | ETL logic in [src/etl.py](../src/etl.py), DB config in [src/db.py](../src/db.py), PostgreSQL stack in [docker-compose.yml](../docker-compose.yml) | Docker stack verified healthy; ETL run confirmed in dashboard container logs |
| Compute on-time delivery rate KPI | Complete | [src/kpis.py](../src/kpis.py) function [kpi_summary](../src/kpis.py) | KPI rendered in dashboard card in [dashboard/app.py](../dashboard/app.py) |
| Compute order cycle time KPI | Complete | [src/kpis.py](../src/kpis.py) function [kpi_summary](../src/kpis.py) | KPI rendered in dashboard card in [dashboard/app.py](../dashboard/app.py) |
| Compute inventory accuracy KPI | Complete | [src/kpis.py](../src/kpis.py) function [inventory_accuracy](../src/kpis.py) | KPI rendered in dashboard card in [dashboard/app.py](../dashboard/app.py) |
| Dashboard frontend in React or Streamlit | Complete | Streamlit dashboard in [dashboard/app.py](../dashboard/app.py) | Dashboard served on port 8501 in Docker |
| Chart: orders by day | Complete | [dashboard/app.py](../dashboard/app.py), data prep in [src/kpis.py](../src/kpis.py) | Chart plotted via Plotly bar |
| Chart: backlog trend | Complete | [dashboard/app.py](../dashboard/app.py), data prep in [src/kpis.py](../src/kpis.py) | Chart plotted via Plotly line |
| Chart: late-order trends | Complete | [dashboard/app.py](../dashboard/app.py), data prep in [src/kpis.py](../src/kpis.py) | Chart plotted via Plotly line |
| Filters: warehouse, date range, customer | Complete | Sidebar filter controls in [dashboard/app.py](../dashboard/app.py) | Filtered dataframe and charts update by selection |
| Export to CSV from app | Complete | Download button in [dashboard/app.py](../dashboard/app.py) | Exports filtered shipments CSV |
| Export to Excel from app | Complete | Excel writer + download button in [dashboard/app.py](../dashboard/app.py) | Exports KPI summary + filtered shipments workbook |
| Weekly Project Report sample (Word or Markdown) | Complete | [reports/weekly-project-report.md](../reports/weekly-project-report.md) | Report file present and populated |
| Optional simple task automation for refresh | Complete | [scripts/refresh_metrics.py](../scripts/refresh_metrics.py), [scripts/nightly_refresh.ps1](../scripts/nightly_refresh.ps1) | Script executes KPI refresh/snapshot path |

## Additional Deliverables (Beyond Required Scope)
- Dockerized deployment: [Dockerfile](../Dockerfile), [docker-compose.yml](../docker-compose.yml)
- Health check and CI workflow: [scripts/check_health.ps1](../scripts/check_health.ps1), [.github/workflows/docker-healthcheck.yml](../.github/workflows/docker-healthcheck.yml)
- CLI weekly export automation: [scripts/export_weekly_report.py](../scripts/export_weekly_report.py)
- Operational runbook: [docs/operations/operations-runbook.md](../docs/operations/operations-runbook.md)
- Demo release checklist: [docs/governance/demo-day-checklist.md](../docs/governance/demo-day-checklist.md)
