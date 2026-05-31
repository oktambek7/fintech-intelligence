# Fintech Transaction Intelligence Platform

An end-to-end data engineering and analytics project simulating a real-world
fintech environment — from raw data generation to a live cloud-connected dashboard.

---

## Architecture

Python (Data Generation)
↓
Python (ETL & Transformation)
↓
Google BigQuery (Cloud Data Warehouse)
↓
Power BI (Live Dashboard)

---

## Project Structure

fintech-intelligence/
│
├── generate_data.py       # Synthetic data generation (1K customers, 50K transactions)
├── transform.py           # ETL pipeline — cleaning, enrichment, feature engineering
├── upload_to_bq.py        # BigQuery upload pipeline
│
├── raw/                   # Raw generated CSVs (gitignored)
├── processed/             # Transformed CSVs (gitignored)
│
└── README.md

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data Generation | Python (Faker, NumPy, Pandas) |
| Transformation | Python (Pandas) |
| Cloud Warehouse | Google BigQuery |
| Analytics | SQL (CTEs, Window Functions, Aggregations) |
| Visualization | Power BI (Live BigQuery connection) |

---

## Dataset

Synthetic but realistic fintech dataset:
- **1,000 customers** across 5 countries (UZ, KZ, RU, TR, AE)
- **50,000 transactions** over 2 years (2023–2024)
- Customer segments: Premium, Standard, Basic
- Transaction categories: Transfer, Payment, Withdrawal, Deposit, Refund
- Channels: Mobile, Web, ATM, Branch
- Fraud injected at ~2% rate with realistic patterns (late-night + high amount)

---

## Key Findings

- **Fraud concentrates between 1–4 AM** — 100% of flagged transactions occur at night
- **Mobile dominates** with 55% of total volume ($9.56M out of $17.48M)
- **Standard segment** drives 49% of all transactions by volume
- **UZ market** accounts for $8.3M revenue — largest single market
- **Gen X and Boomers** generate the highest revenue despite fewer transactions

---

## Pipeline Steps

### 1. Data Generation (`generate_data.py`)
- Generates realistic customers with segments, countries, age groups
- Generates transactions with time patterns, amounts scaled by segment
- Injects fraud with realistic behavioral signals

### 2. Transformation (`transform.py`)
- Removes failed transactions and zero-amount records
- Enriches with time features: hour, day part, weekday, quarter
- Builds customer summary table with aggregated KPIs
- Joins transactions with customer data into master table

### 3. BigQuery Upload (`upload_to_bq.py`)
- Authenticates via service account
- Uploads 3 tables: `master_transactions`, `customer_summary`, `customers`
- Uses WRITE_TRUNCATE for idempotent reloads

### 4. SQL Analytics (BigQuery Console)
Five analytical queries covering:
- Monthly revenue trends
- Segment performance
- Top customers by spend
- Fraud patterns by hour
- Channel efficiency by category

### 5. Power BI Dashboard
Two-page live dashboard connected directly to BigQuery:
- **Page 1 — Transaction Overview**: Revenue trend, fraud analysis, channel matrix, KPIs
- **Page 2 — Customer Intelligence**: Geographic distribution, age group revenue, top customers

---

## How to Run

1. Clone the repo
2. Install dependencies:
```bash
   pip install faker pandas numpy google-cloud-bigquery[pandas] pyarrow
```
3. Add your `service_account.json` to project root (not committed)
4. Update `PROJECT_ID` in `upload_to_bq.py`
5. Run in order:
```bash
   python generate_data.py
   python transform.py
   python upload_to_bq.py
```
6. Open Power BI and connect to your BigQuery dataset

---

## Dashboard Preview

*(Add screenshots of your Power BI dashboard here)*

---

*Built as a portfolio project demonstrating end-to-end data engineering and analytics skills.*
