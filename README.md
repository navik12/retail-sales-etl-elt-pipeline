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
                              GitHub Actions:
                                CI  -> pytest on every push
                                CD  -> build & publish Docker image (ghcr.io)
                              Dashboard (KPIs)
```

## Build levels

| Level | Stage | Status |
|-------|-------|--------|
| 1 | Extract (CSV + Fake Store API -> `data/raw/`) | ✅ done (`v1.0.0`) |
| 2 | ETL: transform, validate & load into PostgreSQL + metadata logging | ✅ done (`v2.0.0`) |
| 3 | ELT: load raw to Postgres, then transform + build KPI tables in SQL | ✅ done (`v3.0.0`) |
| 4 | Orchestration: Airflow DAG runs extract→transform→validate→load @daily | ✅ done (`v4.0.0`) |
| 5 | CI/CD: GitHub Actions runs pytest, then builds & publishes a Docker image | ✅ done (`v5.0.0`) |
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

## Level 5 — CI/CD (GitHub Actions)

Every push to GitHub runs `.github/workflows/ci.yml`, which has two jobs:

- **CI (`test`)** — spins up a clean Linux machine, installs Python 3.12 and the
  dependencies, and runs the pytest suite (`tests/test_transform.py`). If any
  test fails, the workflow goes red and the deploy is skipped.
- **CD (`deploy`)** — only runs on `main` **after** the tests pass. It builds the
  pipeline into a Docker image (see `Dockerfile`) and publishes it to the GitHub
  Container Registry, so there's always a tested, runnable, deployable artifact.

```
push -> [ test: pytest ] --pass--> [ deploy: build & push Docker image ]
                          --fail--> stop (deploy never runs)
```

Run the tests locally with:

```bash
pytest -v
```

### Docker image

The published image bundles the code and its dependencies so the pipeline runs
identically anywhere:

```bash
docker pull ghcr.io/navik12/retail-sales-etl-elt-pipeline:latest
docker run --rm ghcr.io/navik12/retail-sales-etl-elt-pipeline:latest
```

(The container still needs a database to connect to via environment variables —
the image just packages the code and dependencies.)
