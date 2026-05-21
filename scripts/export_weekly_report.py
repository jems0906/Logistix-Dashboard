from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import pandas as pd
from sqlalchemy.exc import OperationalError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.etl import refresh_all
from src.kpis import apply_filters, backlog_by_day, kpi_summary, late_orders_trend, load_inventory, load_shipments, orders_by_day


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def _fmt_hours(value: float) -> str:
    return f"{value:.1f} hrs"


def generate_weekly_report(output_dir: Path, lookback_days: int = 7) -> dict[str, Path]:
    try:
        shipments = load_shipments()
        inventory = load_inventory()
    except OperationalError:
        # Bootstrap local DB automatically so report export works without manual ETL.
        refresh_all(ROOT / "data")
        shipments = load_shipments()
        inventory = load_inventory()

    shipments["created_at"] = pd.to_datetime(shipments["created_at"], errors="coerce")

    end_date = pd.Timestamp(date.today())
    start_date = end_date - pd.Timedelta(days=lookback_days - 1)

    filtered = apply_filters(
        shipments,
        start_date=start_date,
        end_date=end_date,
    )

    summary = kpi_summary(filtered, inventory)
    orders_day = orders_by_day(filtered)
    backlog_day = backlog_by_day(filtered)
    late_day = late_orders_trend(filtered)

    output_dir.mkdir(parents=True, exist_ok=True)

    stamp = date.today().isoformat()
    markdown_path = output_dir / f"Weekly_Project_Report_{stamp}.md"
    shipments_csv_path = output_dir / f"weekly_shipments_{stamp}.csv"
    orders_csv_path = output_dir / f"orders_by_day_{stamp}.csv"
    backlog_csv_path = output_dir / f"backlog_by_day_{stamp}.csv"
    late_csv_path = output_dir / f"late_orders_{stamp}.csv"

    filtered.to_csv(shipments_csv_path, index=False)
    orders_day.to_csv(orders_csv_path, index=False)
    backlog_day.to_csv(backlog_csv_path, index=False)
    late_day.to_csv(late_csv_path, index=False)

    lines = [
        f"# Weekly Project Report - {stamp}",
        "",
        f"Reporting window: {start_date.date()} to {end_date.date()}",
        "",
        "## KPI Summary",
        f"- On-time delivery rate: {_fmt_pct(summary['on_time_delivery_rate'])}",
        f"- Average order cycle time: {_fmt_hours(summary['avg_order_cycle_time_hours'])}",
        f"- Inventory accuracy: {_fmt_pct(summary['inventory_accuracy'])}",
        f"- Open orders: {summary['open_orders']}",
        f"- Total orders in window: {summary['total_orders']}",
        "",
        "## Included Data Exports",
        f"- {shipments_csv_path.name}",
        f"- {orders_csv_path.name}",
        f"- {backlog_csv_path.name}",
        f"- {late_csv_path.name}",
        "",
        "## Operational Notes",
        "- Review late-order rows for root-cause categories (carrier delay, pick/pack delay, inventory hold).",
        "- Compare backlog trend with staffing and outbound cut-off capacity.",
        "- Validate top SKU discrepancies from cycle counts before customer commitment updates.",
    ]

    markdown_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "markdown": markdown_path,
        "shipments_csv": shipments_csv_path,
        "orders_csv": orders_csv_path,
        "backlog_csv": backlog_csv_path,
        "late_csv": late_csv_path,
    }


def main() -> None:
    output_dir = Path("reports") / "generated"
    artifacts = generate_weekly_report(output_dir=output_dir, lookback_days=7)

    print("Weekly report artifacts created:")
    for _, file_path in artifacts.items():
        print(f"- {file_path}")


if __name__ == "__main__":
    main()
