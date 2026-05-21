from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.etl import refresh_all
from src.kpis import apply_filters, backlog_by_day, kpi_summary, late_orders_trend, load_inventory, load_shipments, orders_by_day


st.set_page_config(page_title="Logistix Dashboard", page_icon="📦", layout="wide")
st.title("Logistix Operations Dashboard")
st.caption("Shipment and inventory monitoring for customer and warehouse operations teams")


@st.cache_data(ttl=60)
def get_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    shipments = load_shipments()
    inventory = load_inventory()

    shipments["created_at"] = pd.to_datetime(shipments["created_at"], errors="coerce")
    shipments["promised_at"] = pd.to_datetime(shipments["promised_at"], errors="coerce")
    shipments["delivered_at"] = pd.to_datetime(shipments["delivered_at"], errors="coerce")

    return shipments, inventory


with st.sidebar:
    st.header("Filters")

    if st.button("Refresh from source files"):
        refresh_all(ROOT / "data")
        st.cache_data.clear()
        st.success("Data reloaded into SQL from data folder.")

shipments, inventory = get_data()

all_warehouses = sorted(shipments["warehouse"].dropna().unique().tolist())
all_customers = sorted(shipments["customer"].dropna().unique().tolist())

with st.sidebar:
    selected_warehouses = st.multiselect("Warehouse", all_warehouses, default=all_warehouses)
    selected_customers = st.multiselect("Customer", all_customers, default=all_customers)

    min_date = shipments["created_at"].min().date()
    max_date = shipments["created_at"].max().date()
    selected_date_range = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
else:
    start_date, end_date = min_date, max_date

filtered_shipments = apply_filters(
    shipments,
    warehouses=selected_warehouses,
    customers=selected_customers,
    start_date=pd.Timestamp(start_date),
    end_date=pd.Timestamp(end_date),
)

summary = kpi_summary(filtered_shipments, inventory, selected_warehouses)

c1, c2, c3, c4 = st.columns(4)
c1.metric("On-time delivery", f"{summary['on_time_delivery_rate'] * 100:.1f}%")
c2.metric("Avg order cycle time", f"{summary['avg_order_cycle_time_hours']:.1f} hrs")
c3.metric("Inventory accuracy", f"{summary['inventory_accuracy'] * 100:.1f}%")
c4.metric("Open orders", f"{summary['open_orders']}")

orders_day = orders_by_day(filtered_shipments)
backlog_day = backlog_by_day(filtered_shipments)
late_day = late_orders_trend(filtered_shipments)

left, right = st.columns(2)
with left:
    st.subheader("Orders by day")
    fig_orders = px.bar(orders_day, x="order_day", y="orders", title="Order volume trend")
    st.plotly_chart(fig_orders, use_container_width=True)

with right:
    st.subheader("Backlog trend")
    fig_backlog = px.line(backlog_day, x="day", y="backlog_orders", markers=True, title="Open order backlog")
    st.plotly_chart(fig_backlog, use_container_width=True)

st.subheader("Late-order trends")
fig_late = px.line(late_day, x="delivery_day", y="late_orders", markers=True, title="Late delivered orders over time")
st.plotly_chart(fig_late, use_container_width=True)

st.subheader("Filtered shipment data")
st.dataframe(filtered_shipments, use_container_width=True)

csv_bytes = filtered_shipments.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Export filtered shipments (CSV)",
    data=csv_bytes,
    file_name="filtered_shipments.csv",
    mime="text/csv",
)

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    pd.DataFrame([summary]).to_excel(writer, sheet_name="KPI Summary", index=False)
    filtered_shipments.to_excel(writer, sheet_name="Filtered Shipments", index=False)

st.download_button(
    label="Export KPI + shipment report (Excel)",
    data=excel_buffer.getvalue(),
    file_name="logistix_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
