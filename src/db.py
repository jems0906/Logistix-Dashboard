import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///warehouse.db")

    # Render often provides postgres:// URLs; SQLAlchemy expects postgresql+psycopg2://
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)

    return url


def get_engine() -> Engine:
    return create_engine(get_database_url(), future=True)
