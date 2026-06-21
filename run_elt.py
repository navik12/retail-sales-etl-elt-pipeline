"""
run_elt.py — the ELT ORCHESTRATOR.

ELT order:  Extract + Load RAW  ->  Transform with SQL

    1. load raw CSV/API into Postgres (raw_sales, raw_products) — no cleaning
    2. run sql/transform.sql, which cleans + builds KPI tables inside the DB

Compare with run_etl.py: same data, opposite philosophy. ETL cleans in Python
before loading; ELT loads raw, then cleans in SQL. Run:  python3 run_elt.py
"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import text

from config.db import get_engine
from src.extract_load import load_raw_sales, load_raw_products
from src.metadata_logger import log_run

SQL_FILE = Path(__file__).resolve().parent / "sql" / "transform.sql"
PIPELINE_NAME = "retail_sales_elt"


def run_sql_file(engine, path: Path) -> int:
    """Execute every statement in a .sql file. Returns how many ran."""
    statements = [s.strip() for s in path.read_text().split(";") if s.strip()]
    with engine.begin() as conn:  # one transaction for the whole script
        for stmt in statements:
            conn.execute(text(stmt))
    return len(statements)


def main() -> None:
    engine = get_engine()
    started_at = datetime.now()
    status = "success"
    row_count = 0

    try:
        print("=== Retail Sales ELT ===\n")

        print("[1/2] Extract + Load RAW")
        load_raw_sales(engine)
        load_raw_products(engine)

        print("\n[2/2] Transform in SQL")
        n = run_sql_file(engine, SQL_FILE)
        with engine.connect() as conn:
            row_count = conn.execute(text("SELECT count(*) FROM clean_sales")).scalar()
        print(f"Ran {n} SQL statements; clean_sales now has {row_count:,} rows")

    except Exception as exc:
        status = "failed"
        print(f"\nELT FAILED: {exc}")
        raise
    finally:
        finished_at = datetime.now()
        log_run(engine, PIPELINE_NAME, "clean_sales",
                row_count, status, started_at, finished_at)
        print(f"\nDone. Status: {status}")


if __name__ == "__main__":
    main()
