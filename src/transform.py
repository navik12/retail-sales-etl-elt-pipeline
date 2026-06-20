"""
TRANSFORM — the "T" in ETL.

Takes the RAW Superstore DataFrame and returns a CLEAN one:
  - rename columns to tidy snake_case (Order Date -> order_date)
  - parse the date columns from text into real dates
  - drop rows that are missing any essential field
  - add derived columns: unit_price and revenue

Note on "revenue": in the Superstore dataset the `sales` column is ALREADY the
line-item revenue (quantity x unit price). So revenue = sales, and we also derive
unit_price = sales / quantity. (Knowing your data instead of blindly applying a
formula is a good thing to be able to explain in an interview.)
"""

import pandas as pd

# The fields that MUST be present for a row to be usable downstream.
KEY_COLUMNS = ["row_id", "order_id", "order_date", "sales", "quantity"]


def _to_snake(name: str) -> str:
    """'Sub-Category' -> 'sub_category'."""
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def transform_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw sales DataFrame and add derived columns."""
    df = df.copy()

    # 1. Tidy column names.
    df.columns = [_to_snake(c) for c in df.columns]

    # 2. Convert date text (e.g. "11/8/2016") into real datetime values.
    #    errors="coerce" turns anything unparseable into NaT so we can drop it.
    df["order_date"] = pd.to_datetime(df["order_date"], format="%m/%d/%Y", errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], format="%m/%d/%Y", errors="coerce")

    # 3. Drop rows missing any essential field.
    before = len(df)
    df = df.dropna(subset=KEY_COLUMNS)
    dropped = before - len(df)

    # 4. Derived columns.
    df["unit_price"] = (df["sales"] / df["quantity"]).round(2)
    df["revenue"] = df["sales"].round(2)

    print(f"Transform: {len(df):,} clean rows ({dropped} dropped for missing keys)")
    return df
