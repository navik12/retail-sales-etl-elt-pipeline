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
| 2 | Transform, validate & load into PostgreSQL + metadata logging | ✅ done (`v2.0.0`) |
| 3 | Analytics SQL queries / views | ⏳ |
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
