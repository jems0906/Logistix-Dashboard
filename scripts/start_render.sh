#!/usr/bin/env bash
set -euo pipefail

# Load/refresh sample source data into SQL before starting Streamlit.
python run_etl.py

streamlit run dashboard/app.py \
  --server.address=0.0.0.0 \
  --server.port="${PORT}" \
  --browser.gatherUsageStats=false
