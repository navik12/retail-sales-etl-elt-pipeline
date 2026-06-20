"""
METADATA LOGGER — records a row in `pipeline_logs` every time the ETL runs.

This is the "observability" part: when did the pipeline run, how many rows did
it load, did it succeed or fail, and how long did it take? Real data teams rely
on exactly this kind of log to monitor pipelines and debug failures.
"""

from datetime import datetime

from sqlalchemy import text
from sqlalchemy.engine import Engine

# Create the log table once if it doesn't already exist.
CREATE_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS pipeline_logs (
    id               SERIAL PRIMARY KEY,
    pipeline_name    TEXT,
    table_name       TEXT,
    row_count        INTEGER,
    status           TEXT,
    started_at       TIMESTAMP,
    finished_at      TIMESTAMP,
    duration_seconds NUMERIC
);
"""

INSERT_LOG = """
INSERT INTO pipeline_logs
    (pipeline_name, table_name, row_count, status,
     started_at, finished_at, duration_seconds)
VALUES
    (:pipeline_name, :table_name, :row_count, :status,
     :started_at, :finished_at, :duration_seconds);
"""


def log_run(engine: Engine, pipeline_name: str, table_name: str,
            row_count: int, status: str,
            started_at: datetime, finished_at: datetime) -> None:
    """Insert one record describing this pipeline run."""
    duration = (finished_at - started_at).total_seconds()
    with engine.begin() as conn:  # begin() = auto-commit on success
        conn.execute(text(CREATE_LOGS_TABLE))
        conn.execute(text(INSERT_LOG), {
            "pipeline_name": pipeline_name,
            "table_name": table_name,
            "row_count": row_count,
            "status": status,
            "started_at": started_at,
            "finished_at": finished_at,
            "duration_seconds": duration,
        })
    print(f"Metadata: logged run (status={status}, rows={row_count}, {duration:.2f}s)")
