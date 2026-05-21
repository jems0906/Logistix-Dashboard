from datetime import date
from pathlib import Path

from src.etl import refresh_all
from src.kpis import kpi_summary, load_inventory, load_shipments, snapshot_kpis


def run_refresh() -> None:
    refresh_all(Path("data"))
    shipments = load_shipments()
    inventory = load_inventory()

    summary = kpi_summary(shipments, inventory)
    snapshot_kpis(summary, snapshot_date=date.today())

    print("Metrics refresh complete and KPI snapshot recorded.")


if __name__ == "__main__":
    run_refresh()
