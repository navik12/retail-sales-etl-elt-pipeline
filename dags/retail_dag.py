"""
Airflow DAG — Retail Sales ETL
==============================
This turns our manual pipeline into a SCHEDULED, automated workflow.

It runs the four ETL stages in order, once a day:

    extract  >>  transform  >>  validate  >>  load

Each stage is an Airflow "task". The ">>" arrows tell Airflow the order: a task
only starts after the one before it succeeds. If a stage fails, the ones after it
are skipped and Airflow shows that task in red.

How the tasks pass data:
    Airflow tasks run as separate processes, so we DON'T pass big DataFrames
    between them in memory. Instead each task writes its result to a small staging
    file in data/processed/, and the next task reads it. (This is a normal,
    realistic pattern.)
"""

import os
import sys
from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator

# --- Make our project code importable from inside Airflow -------------------
# The DAG file lives in <project>/dags/, so the project root is one level up.
# We add it to sys.path so "from src...." and "from config...." work.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config.db import get_engine
from src.extract import extract_csv
from src.transform import transform_sales
from src.validation.checks import run_checks
from src.load import load_dataframe
from src.metadata_logger import log_run

# Small staging files the tasks use to hand data to one another.
RAW_STAGE = os.path.join(PROJECT_ROOT, "data", "processed", "stage_raw.pkl")
CLEAN_STAGE = os.path.join(PROJECT_ROOT, "data", "processed", "stage_clean.pkl")
TARGET_TABLE = "sales"


# --- One Python function per stage -----------------------------------------
def _extract(**_):
    df = extract_csv()
    df.to_pickle(RAW_STAGE)          # save for the transform task


def _transform(**_):
    df = pd.read_pickle(RAW_STAGE)
    clean = transform_sales(df)
    clean.to_pickle(CLEAN_STAGE)     # save for validate + load tasks


def _validate(**_):
    df = pd.read_pickle(CLEAN_STAGE)
    run_checks(df)                   # raises -> task fails -> load is skipped


def _load(**_):
    df = pd.read_pickle(CLEAN_STAGE)
    engine = get_engine()
    started = datetime.now()
    rows = load_dataframe(df, TARGET_TABLE, engine)
    log_run(engine, "retail_sales_etl_airflow", TARGET_TABLE,
            rows, "success", started, datetime.now())


# --- Settings applied to every task ----------------------------------------
default_args = {
    "owner": "navya",
    "retries": 1,                          # if a task fails, try once more
    "retry_delay": timedelta(minutes=2),   # wait 2 min before retrying
}

# --- The DAG itself ---------------------------------------------------------
with DAG(
    dag_id="retail_sales_etl",
    description="Daily retail sales ETL: extract -> transform -> validate -> load",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),       # earliest date Airflow will schedule
    schedule="@daily",                     # run once every day
    catchup=False,                         # don't back-fill all past days
    tags=["retail", "etl"],
) as dag:

    extract = PythonOperator(task_id="extract", python_callable=_extract)
    transform = PythonOperator(task_id="transform", python_callable=_transform)
    validate = PythonOperator(task_id="validate", python_callable=_validate)
    load = PythonOperator(task_id="load", python_callable=_load)

    # This single line defines the whole pipeline order:
    extract >> transform >> validate >> load
