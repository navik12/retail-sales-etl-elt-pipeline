"""
VALIDATION — data-quality gate.

Before we load anything into the database, we assert that the data meets our
rules. If any rule fails, the pipeline stops with a clear error instead of
silently loading bad data. This is what makes a pipeline trustworthy.

Important grain note: in Superstore, one ORDER contains many product lines, so
`order_id` legitimately repeats. The true unique key per row is `row_id` — that's
what we check for duplicates (NOT order_id, which the generic plan assumed).
"""

import pandas as pd

# Columns that must never contain a missing value.
KEY_COLUMNS = ["row_id", "order_id", "order_date", "sales", "quantity", "revenue"]


def run_checks(df: pd.DataFrame) -> bool:
    """Run all data-quality checks. Raises AssertionError on the first failure."""

    # 1. We must actually have data.
    assert len(df) > 0, "Validation failed: the dataset is empty"

    # 2. No missing values in key columns.
    for col in KEY_COLUMNS:
        nulls = int(df[col].isna().sum())
        assert nulls == 0, f"Validation failed: {nulls} null(s) in '{col}'"

    # 3. row_id must be unique (the real primary key).
    dupes = int(df["row_id"].duplicated().sum())
    assert dupes == 0, f"Validation failed: {dupes} duplicate row_id value(s)"

    # 4. Sanity checks on the numbers.
    assert (df["quantity"] > 0).all(), "Validation failed: found non-positive quantity"
    assert (df["sales"] >= 0).all(), "Validation failed: found negative sales"

    print(f"Validation passed: {len(df):,} rows, key columns clean, row_id unique")
    return True
