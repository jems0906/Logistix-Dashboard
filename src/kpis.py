from __future__ import annotations

from datetime import date

import pandas as pd
from sqlalchemy import text

from src.db import get_engine


def load_shipments() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM shipments", engine)


def load_inventory() -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql("SELECT * FROM inventory", engine)


def apply_filters(
    shipments: pd.DataFrame,
    warehouses: list[str] | None = None,
    customers: list[str] | None = None,
    start_date: pd.Timestamp | None = None,
    end_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    df = shipments.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df["promised_at"] = pd.to_datetime(df["promised_at"], errors="coerce")
    df["delivered_at"] = pd.to_datetime(df["delivered_at"], errors="coerce")

    if warehouses:
        df = df[df["warehouse"].isin(warehouses)]
    if customers:
        df = df[df["customer"].isin(customers)]
    if start_date is not None:
        df = df[df["created_at"] >= pd.Timestamp(start_date)]
    if end_date is not None:
        df = df[df["created_at"] <= pd.Timestamp(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)]

    return df


def inventory_accuracy(inventory: pd.DataFrame, warehouses: list[str] | None = None) -> float:
    df = inventory.copy()
    if warehouses:
        df = df[df["warehouse"].isin(warehouses)]
    if df.empty:
        return 0.0

    total_system = df["system_qty"].sum()
    if total_system == 0:
        return 0.0

    total_abs_error = (df["system_qty"] - df["counted_qty"]).abs().sum()
    score = 1 - (total_abs_error / total_system)
    return max(0.0, float(score))


def kpi_summary(filtered_shipments: pd.DataFrame, inventory: pd.DataFrame, warehouses: list[str] | None = None) -> dict:
    delivered = filtered_shipments[filtered_shipments["delivered_at"].notna()].copy()

    if not delivered.empty:
        delivered["on_time"] = delivered["delivered_at"] <= delivered["promised_at"]
        on_time_rate = delivered["on_time"].mean()
        avg_cycle_time_hours = (
            (delivered["delivered_at"] - delivered["created_at"]).dt.total_seconds().mean() / 3600
        )
    else:
        on_time_rate = 0.0
        avg_cycle_time_hours = 0.0

    open_orders = filtered_shipments[filtered_shipments["delivered_at"].isna()].shape[0]

    return {
        "on_time_delivery_rate": float(on_time_rate),
        "avg_order_cycle_time_hours": float(avg_cycle_time_hours),
        "inventory_accuracy": inventory_accuracy(inventory, warehouses),
        "open_orders": int(open_orders),
        "total_orders": int(filtered_shipments.shape[0]),
    }


def orders_by_day(filtered_shipments: pd.DataFrame) -> pd.DataFrame:
    chart = filtered_shipments.copy()
    chart["order_day"] = chart["created_at"].dt.date
    return chart.groupby("order_day", as_index=False).size().rename(columns={"size": "orders"})


def backlog_by_day(filtered_shipments: pd.DataFrame) -> pd.DataFrame:
    if filtered_shipments.empty:
        return pd.DataFrame(columns=["day", "backlog_orders"])

    start_day = filtered_shipments["created_at"].min().date()
    end_day = pd.Timestamp.today().date()
    days = pd.date_range(start_day, end_day, freq="D")

    backlog_rows = []
    for day in days:
        open_as_of_day = filtered_shipments[
            (filtered_shipments["created_at"] <= day)
            & (
                filtered_shipments["delivered_at"].isna()
                | (filtered_shipments["delivered_at"] > day)
            )
        ]
        backlog_rows.append({"day": day.date(), "backlog_orders": open_as_of_day.shape[0]})

    return pd.DataFrame(backlog_rows)


def late_orders_trend(filtered_shipments: pd.DataFrame) -> pd.DataFrame:
    delivered = filtered_shipments[filtered_shipments["delivered_at"].notna()].copy()
    if delivered.empty:
        return pd.DataFrame(columns=["delivery_day", "late_orders"])

    delivered["is_late"] = delivered["delivered_at"] > delivered["promised_at"]
    delivered["delivery_day"] = delivered["delivered_at"].dt.date

    late = delivered[delivered["is_late"]]
    return late.groupby("delivery_day", as_index=False).size().rename(columns={"size": "late_orders"})


def snapshot_kpis(kpis: dict, snapshot_date: date | None = None) -> None:
    engine = get_engine()
    snapshot_date = snapshot_date or date.today()

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO kpi_snapshots (
                    snapshot_date,
                    on_time_delivery_rate,
                    avg_cycle_time_hours,
                    inventory_accuracy,
                    open_orders,
                    total_orders
                ) VALUES (
                    :snapshot_date,
                    :on_time_delivery_rate,
                    :avg_cycle_time_hours,
                    :inventory_accuracy,
                    :open_orders,
                    :total_orders
                )
                """
            ),
            {
                "snapshot_date": snapshot_date,
                "on_time_delivery_rate": kpis["on_time_delivery_rate"],
                "avg_cycle_time_hours": kpis["avg_order_cycle_time_hours"],
                "inventory_accuracy": kpis["inventory_accuracy"],
                "open_orders": kpis["open_orders"],
                "total_orders": kpis["total_orders"],
            },
        )
