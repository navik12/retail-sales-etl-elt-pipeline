"""
EXTRACT + LOAD (the "EL" of ELT)
================================
The ELT philosophy: get the raw data into the database AS-IS, with NO cleaning,
then let SQL do all the transforming later (see sql/transform.sql).

So here we just dump:
  - the Superstore CSV  -> raw_sales     (every column loaded as plain TEXT)
  - the Fake Store API  -> raw_products  (every column loaded as plain TEXT)

Loading everything as text (dtype=str) is the key trick: we do ZERO type
conversion or cleaning in Python. Dates stay as "11/8/2016" strings, numbers stay
as "261.96" strings. SQL will cast and clean them in the next step.
"""

import json
from pathlib import Path

import pandas as pd
from sqlalchemy.engine import Engine

from config.db import get_engine

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CSV_PATH = RAW_DIR / "superstore_sales.csv"
PRODUCTS_JSON = RAW_DIR / "fakestore_products.json"


def _to_snake(name: str) -> str:
    """Tidy ONLY the column name (identifier), never the values."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def load_raw_sales(engine: Engine) -> int:
    """Dump the Superstore CSV into raw_sales with no cleaning at all."""
    # dtype=str => load EVERYTHING as text, so nothing is parsed or changed.
    df = pd.read_csv(CSV_PATH, encoding="latin-1", dtype=str)
    df.columns = [_to_snake(c) for c in df.columns]
    df.to_sql("raw_sales", engine, if_exists="replace", index=False)
    print(f"raw_sales   : loaded {len(df):,} raw rows (all text, uncleaned)")
    return len(df)


def load_raw_products(engine: Engine) -> int:
    """Dump the Fake Store API products into raw_products with no cleaning."""
    with open(PRODUCTS_JSON) as f:
        products = json.load(f)
    df = pd.json_normalize(products)              # flatten nested rating.* fields
    df.columns = [_to_snake(c) for c in df.columns]
    df = df.astype(str)                           # keep everything raw text
    df.to_sql("raw_products", engine, if_exists="replace", index=False)
    print(f"raw_products: loaded {len(df)} raw rows (all text, uncleaned)")
    return len(df)


def main() -> None:
    engine = get_engine()
    print("=== ELT step 1: Extract + Load RAW (no cleaning) ===\n")
    load_raw_sales(engine)
    load_raw_products(engine)
    print("\nRaw data landed in Postgres. Cleaning happens in SQL (transform.sql).")


if __name__ == "__main__":
    main()
