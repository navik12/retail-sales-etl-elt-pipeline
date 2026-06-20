"""
Level 1 — EXTRACT
=================
The first stage of the ETL pipeline. Its only job is to pull raw data from our
two sources and land it, untouched, in `data/raw/`.

  Sources:
    1. Superstore CSV   (a Kaggle retail dataset, downloaded manually)
    2. Fake Store API   (a free public API -> https://fakestoreapi.com)

We do NOT clean or change anything here. "Extract" means: get the raw data and
save a faithful copy. Cleaning happens in Level 2 (transform).

Run it with:   python3 src/extract.py
"""

import json
from pathlib import Path

import pandas as pd
import requests

# Project paths. Path(__file__) is this file; .parent.parent is the project root.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CSV_PATH = RAW_DIR / "superstore_sales.csv"
API_URL = "https://fakestoreapi.com/products"
API_OUTPUT = RAW_DIR / "fakestore_products.json"


def extract_csv() -> pd.DataFrame:
    """Load the Superstore CSV into a DataFrame and report what we got."""
    # encoding="latin-1": the Superstore file has a few non-UTF-8 characters.
    df = pd.read_csv(CSV_PATH, encoding="latin-1")
    print(f"CSV  : loaded {len(df):,} rows x {len(df.columns)} columns from {CSV_PATH.name}")
    return df


def extract_api() -> list:
    """Pull product data from the Fake Store API and save the raw JSON."""
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()  # turn any HTTP error (404/500) into an exception
    products = response.json()

    # Make sure the landing folder exists, then save the raw response verbatim.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(API_OUTPUT, "w") as f:
        json.dump(products, f, indent=2)

    print(f"API  : fetched {len(products)} products -> {API_OUTPUT.name}")
    return products


def main() -> None:
    print("Starting EXTRACT stage...\n")
    extract_csv()
    extract_api()
    print("\nExtract complete. Raw data is in data/raw/")


if __name__ == "__main__":
    main()
