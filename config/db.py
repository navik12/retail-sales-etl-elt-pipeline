"""
Database connection — one single place that knows how to reach PostgreSQL.

Every other file (load, metadata_logger, run_etl) asks THIS file for a
connection, so if the database details ever change, we change them in one spot.

Defaults match a local Homebrew PostgreSQL (user = your Mac name, no password).
You can override any of them with environment variables, which is how you'd
supply real credentials in CI/CD or production without hard-coding secrets.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_engine() -> Engine:
    """Build and return a SQLAlchemy engine for the retail database."""
    user = os.getenv("PGUSER", "navya")
    password = os.getenv("PGPASSWORD", "")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    database = os.getenv("PGDATABASE", "retail")

    # Only include ":password" if one was actually provided.
    auth = f"{user}:{password}" if password else user
    url = f"postgresql+psycopg2://{auth}@{host}:{port}/{database}"
    return create_engine(url)
