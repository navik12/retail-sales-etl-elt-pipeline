"""
LOAD — the "L" in ETL.

Pushes the clean DataFrame into a PostgreSQL table using pandas' to_sql.
We use if_exists="replace" so re-running the pipeline gives a fresh, consistent
table every time (idempotent) — important for a scheduled daily job.
"""

import pandas as pd
from sqlalchemy.engine import Engine


def load_dataframe(df: pd.DataFrame, table_name: str, engine: Engine,
                   if_exists: str = "replace") -> int:
    """Write the DataFrame to `table_name` and return the number of rows loaded."""
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    print(f"Load: wrote {len(df):,} rows into table '{table_name}'")
    return len(df)
