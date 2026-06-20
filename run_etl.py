"""
run_etl.py — the ORCHESTRATOR.

Runs the whole pipeline in order:

    Extract  ->  Transform  ->  Validate  ->  Load  ->  log metadata

If any stage fails, we still log a "failed" record so there's always a trace of
what happened. Run it with:   python3 run_etl.py
"""

from datetime import datetime

from config.db import get_engine
from src.extract import extract_csv
from src.transform import transform_sales
from src.validation.checks import run_checks
from src.load import load_dataframe
from src.metadata_logger import log_run

PIPELINE_NAME = "retail_sales_etl"
TARGET_TABLE = "sales"


def main() -> None:
    engine = get_engine()
    started_at = datetime.now()
    status = "success"
    row_count = 0

    try:
        print("=== Retail Sales ETL ===\n")

        print("[1/4] Extract")
        raw_df = extract_csv()

        print("\n[2/4] Transform")
        clean_df = transform_sales(raw_df)

        print("\n[3/4] Validate")
        run_checks(clean_df)

        print("\n[4/4] Load")
        row_count = load_dataframe(clean_df, TARGET_TABLE, engine)

    except Exception as exc:
        status = "failed"
        print(f"\nPipeline FAILED: {exc}")
        raise
    finally:
        finished_at = datetime.now()
        log_run(engine, PIPELINE_NAME, TARGET_TABLE,
                row_count, status, started_at, finished_at)
        print(f"\nDone. Status: {status}")


if __name__ == "__main__":
    main()
