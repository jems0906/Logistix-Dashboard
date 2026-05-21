from pathlib import Path

from src.etl import refresh_all


if __name__ == "__main__":
    shipments, inventory = refresh_all(Path("data"))
    print(f"ETL finished: {len(shipments)} shipments, {len(inventory)} inventory rows loaded.")
