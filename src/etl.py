from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db import get_engine


DATE_COLUMNS = ["created_at", "promised_at", "shipped_at", "delivered_at", "last_counted_at"]


def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


def load_shipments(file_path: Path) -> pd.DataFrame:
    with file_path.open("r", encoding="utf-8") as f:
        records = json.load(f)
    df = pd.DataFrame(records)
    return _parse_dates(df)


def load_inventory(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return _parse_dates(df)


def init_schema() -> None:
    engine = get_engine()
    statements = [
        """
        CREATE TABLE IF NOT EXISTS shipments (
            order_id TEXT PRIMARY KEY,
            warehouse TEXT,
            customer TEXT,
            sku TEXT,
            quantity INTEGER,
            status TEXT,
            created_at TIMESTAMP,
            promised_at TIMESTAMP,
            shipped_at TIMESTAMP,
            delivered_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inventory (
            warehouse TEXT,
            sku TEXT,
            system_qty INTEGER,
            counted_qty INTEGER,
            last_counted_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS kpi_snapshots (
            snapshot_date DATE,
            on_time_delivery_rate DOUBLE PRECISION,
            avg_cycle_time_hours DOUBLE PRECISION,
            inventory_accuracy DOUBLE PRECISION,
            open_orders INTEGER,
            total_orders INTEGER
        )
        """,
    ]
    with engine.begin() as conn:
        for sql in statements:
            conn.execute(text(sql))


def load_to_sql(shipments: pd.DataFrame, inventory: pd.DataFrame) -> None:
    engine = get_engine()
    with engine.begin() as conn:
        shipments.to_sql("shipments", conn, if_exists="replace", index=False)
        inventory.to_sql("inventory", conn, if_exists="replace", index=False)


def refresh_all(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    shipments = load_shipments(data_dir / "shipments.json")
    inventory = load_inventory(data_dir / "inventory.csv")
    init_schema()
    load_to_sql(shipments, inventory)
    return shipments, inventory


def main() -> None:
    parser = argparse.ArgumentParser(description="Load shipment and inventory data into SQL.")
    parser.add_argument("--data-dir", default="data", help="Directory containing shipments.json and inventory.csv")
    args = parser.parse_args()

    shipments, inventory = refresh_all(Path(args.data_dir))
    print(f"Loaded {len(shipments)} shipments and {len(inventory)} inventory rows.")


if __name__ == "__main__":
    main()
