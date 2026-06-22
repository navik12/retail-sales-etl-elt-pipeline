# Automated Retail Sales Analytics Pipeline

An end-to-end data engineering project: ingest retail sales data from an API and
CSV files, transform and validate it, load it into PostgreSQL, orchestrate daily
runs with Airflow, and test everything with GitHub Actions CI/CD.

Built level-by-level as a portfolio piece for Data Analyst / Data Engineer roles.

## Architecture (final goal)

```
CSV + API  ->  Extract  ->  Transform + Validate  ->  Load (PostgreSQL)
                                                          |
                              Airflow (schedule) ---------+
                              GitHub Actions (CI/CD tests)
                              Dashboard (KPIs)
```

## Build levels

| Level | Stage | Status |
|-------|-------|--------|
| 1 | Extract (CSV + Fake Store API -> `data/raw/`) | ✅ done (`v1.0.0`) |
| 2 | ETL: transform, validate & load into PostgreSQL + metadata logging | ✅ done (`v2.0.0`) |
| 3 | ELT: load raw to Postgres, then transform + build KPI tables in SQL | ✅ done (`v3.0.0`) |
| 4 | Orchestration: Airflow DAG runs extract→transform→validate→load @daily | ✅ done (`v4.0.0`) |
| 5 | CI/CD: GitHub Actions runs pytest on every push | ✅ done (`v5.0.0`) |
| 4 | Orchestrate with Airflow | ⏳ |
| 5 | CI/CD with GitHub Actions | ⏳ |
| 6 | Dashboard & polish | ⏳ |

## Data sources

- **Superstore sales** (Kaggle CSV) — `data/raw/superstore_sales.csv`
- **Fake Store API** (https://fakestoreapi.com) — `data/raw/fakestore_products.json`

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Level 1 — Extract

```bash
python3 src/extract.py
```

Loads the Superstore CSV and pulls the Fake Store API, landing both in
`data/raw/`.

## Level 4 — Airflow (orchestration)

Airflow runs in its **own separate virtualenv** (its dependencies conflict with
the project's). Setup notes:

```bash
# separate env so Airflow's pins don't disturb the project .venv
python3 -m venv ~/airflow-venv
source ~/airflow-venv/bin/activate

export AIRFLOW_VERSION=2.10.4
export PYTHON_VERSION=3.12
export CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"

# the DAG's code needs these too. IMPORTANT: pin pandas==2.1.4 — Airflow uses
# SQLAlchemy 1.4, and pandas >= 2.2 breaks `to_sql` against SQLAlchemy 1.4.
pip install "pandas==2.1.4" "sqlalchemy<2.0" psycopg2-binary requests

# point Airflow at this repo's dags/ folder, then launch
export AIRFLOW_HOME=~/airflow
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/dags"   # run from the project root
export AIRFLOW__CORE__LOAD_EXAMPLES=False
airflow standalone
```

Then open http://localhost:8080, un-pause `retail_sales_etl`, and trigger it.
