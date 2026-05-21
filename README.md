# Logistix Dashboard

A Python + Streamlit project that ingests warehouse data, stores it in SQL, computes operational KPIs, and exposes a dashboard with export-ready reports.

## Architecture Overview
```mermaid
flowchart LR
  A[data/shipments.json] --> B[src/etl.py]
  C[data/inventory.csv] --> B[src/etl.py]
  B --> D[(PostgreSQL or SQLite)]
  D --> E[src/kpis.py]
  E --> F[dashboard/app.py]
  F --> G[Streamlit UI]
  E --> H[scripts/export_weekly_report.py]
  H --> I[reports/generated/*]
  J[scripts/refresh_metrics.py] --> D
```

## Features
- Data ingestion from source files:
  - `data/shipments.json`
  - `data/inventory.csv`
- SQL load (PostgreSQL supported, SQLite fallback for local demo)
- KPI calculations:
  - On-time delivery rate
  - Order cycle time
  - Inventory accuracy
- Streamlit dashboard with:
  - Charts for orders by day, backlog, late-order trends
  - Filters by warehouse, date range, customer
- Reporting exports:
  - CSV export of filtered shipments
  - Excel export with KPI summary + filtered data
- Sample customer-facing weekly report:
  - `reports/weekly-project-report.md`
- Operations runbook:
  - `docs/operations/operations-runbook.md`
- Demo-day release checklist:
  - `docs/governance/demo-day-checklist.md`
- Requirement-to-evidence matrix:
  - `docs/governance/requirement-evidence-matrix.md`
- Optional automation:
  - `scripts/refresh_metrics.py`
  - `scripts/nightly_refresh.ps1`
  - `scripts/export_weekly_report.py`

## Sample Dashboard Screenshot
![Logistix Dashboard Sample](docs/screenshots/dashboard-sample.svg)

The sample image is stored at `docs/screenshots/dashboard-sample.svg`.

## Project Structure
```
.
├── dashboard/
│   └── app.py
├── data/
│   ├── shipments.json
│   └── inventory.csv
├── reports/
│   └── weekly-project-report.md
├── docs/
│   ├── governance/
│   │   ├── demo-day-checklist.md
│   │   └── requirement-evidence-matrix.md
│   ├── operations/
│   │   └── operations-runbook.md
│   └── screenshots/
│       └── dashboard-sample.svg
├── scripts/
│   ├── check_health.ps1
│   ├── dev.ps1
│   ├── export_weekly_report.py
│   ├── refresh_metrics.py
│   └── nightly_refresh.ps1
├── src/
│   ├── db.py
│   ├── etl.py
│   └── kpis.py
├── .env.example
├── requirements.txt
└── run_etl.py
```

## 1) Setup
```powershell
cd "d:\project\Logistix Dashboard"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Docker Quick Start (PostgreSQL + Dashboard)
```powershell
cd "d:\project\Logistix Dashboard"
docker compose up --build -d
```

## Deploy on Render
This repository includes a Render Blueprint file: `render.yaml`.

1. Open the Render Blueprint deploy URL:
  `https://render.com/deploy?repo=https://github.com/jems0906/Logistix-Dashboard`
2. Review services created from `render.yaml`:
  - `logistix-postgres` (managed PostgreSQL)
  - `logistix-dashboard` (Python web service)
3. Click **Apply** in Render.
4. When deployment completes, open the Render web service URL.

Render start flow is defined in `scripts/start_render.sh` and will:
- run ETL (`python run_etl.py`) to seed sample data
- start Streamlit on Render's `PORT`

Open the dashboard at `http://localhost:8501`.

Stop the stack:
```powershell
docker compose down
```

Stop and remove database volume (full reset):
```powershell
docker compose down -v
```

### One-command dev helper (PowerShell)
Use `scripts/dev.ps1` for common stack operations:

```powershell
# Start and build
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action up

# Show status
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action status

# Show app logs
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action logs

# Stop stack
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action down

# Full reset (remove volumes)
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Action reset
```

### Health check script
Local/service health check for dashboard availability:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_health.ps1 -Url "http://localhost:8501"
```

### CI health check workflow
GitHub Actions workflow at `.github/workflows/docker-healthcheck.yml`:
- Builds and starts the Docker Compose stack
- Runs `scripts/check_health.ps1`
- Prints service status/logs
- Tears down stack

## 2) Configure Database
Set `DATABASE_URL` in your shell.

### PostgreSQL (recommended)
```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/logistix"
```

### SQLite local fallback
```powershell
$env:DATABASE_URL = "sqlite:///warehouse.db"
```

## 3) Run ETL (load source files into SQL)
```powershell
python run_etl.py
```

## 4) Launch Dashboard
```powershell
streamlit run .\dashboard\app.py
```

## 5) Optional Nightly Refresh
Run once manually:
```powershell
python .\scripts\refresh_metrics.py
```

## 6) Generate Weekly Report Artifacts (CLI)
Create a dated weekly markdown report plus CSV exports from SQL data:

```powershell
python .\scripts\export_weekly_report.py
```

Generated files are written to `reports/generated/`.

Schedule in Windows Task Scheduler with action:
- Program/script: `powershell.exe`
- Add arguments:
  `-ExecutionPolicy Bypass -File "d:\project\Logistix Dashboard\scripts\nightly_refresh.ps1"`

## KPI Definitions
- **On-time delivery rate** = delivered orders where `delivered_at <= promised_at` divided by all delivered orders
- **Order cycle time** = average hours between `created_at` and `delivered_at`
- **Inventory accuracy** = `1 - (sum(abs(system_qty - counted_qty)) / sum(system_qty))`

## Notes
- Source files in `data/` are simulated but realistic operations data.
- You can swap in your own source files if schema columns stay the same.
