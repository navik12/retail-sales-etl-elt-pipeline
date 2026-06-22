"""
Tests for src/transform.py
==========================
These run automatically in CI (GitHub Actions) on every push. They check that
our transform function does what we expect, using a tiny fake dataset — no
database needed, so the tests are fast and run anywhere.

Run them locally with:   pytest -v
"""

import numpy as np
import pandas as pd

from src.transform import transform_sales


def _raw_sample() -> pd.DataFrame:
    """A tiny DataFrame shaped like the raw Superstore CSV (original column names)."""
    return pd.DataFrame({
        "Row ID": [1, 2, 3],
        "Order ID": ["CA-1", "CA-1", "CA-2"],   # note: Order ID repeats (same order, 2 lines)
        "Order Date": ["11/8/2016", "12/1/2016", "1/2/2017"],
        "Ship Date": ["11/11/2016", "12/3/2016", "1/5/2017"],
        "Sales": [100.0, 50.0, 30.0],
        "Quantity": [2, 5, 3],
    })


def test_columns_are_renamed_to_snake_case():
    out = transform_sales(_raw_sample())
    # "Order Date" should become "order_date", etc.
    for col in ["row_id", "order_id", "order_date", "ship_date", "sales", "quantity"]:
        assert col in out.columns


def test_dates_are_parsed_to_datetime():
    out = transform_sales(_raw_sample())
    assert pd.api.types.is_datetime64_any_dtype(out["order_date"])


def test_revenue_and_unit_price_are_added():
    out = transform_sales(_raw_sample())
    assert "revenue" in out.columns
    assert "unit_price" in out.columns
    # revenue == sales
    assert out["revenue"].tolist() == [100.0, 50.0, 30.0]
    # unit_price == sales / quantity  (100/2=50, 50/5=10, 30/3=10)
    assert out["unit_price"].tolist() == [50.0, 10.0, 10.0]


def test_rows_missing_key_fields_are_dropped():
    raw = _raw_sample()
    raw.loc[1, "Sales"] = None   # make one row's Sales missing
    out = transform_sales(raw)
    # that row should be dropped -> 2 rows left instead of 3
    assert len(out) == 2
    assert out["sales"].notna().all()


def test_zero_quantity_rows_are_dropped():
    raw = _raw_sample()
    raw.loc[1, "Quantity"] = 0   # divide-by-zero would happen on this row
    out = transform_sales(raw)
    # that row should be dropped -> 2 rows left instead of 3
    assert len(out) == 2
    # and no unit_price should be infinite (proof the guard worked)
    assert np.isfinite(out["unit_price"]).all()
