import pandas as pd
from google.cloud import bigquery
import os

# ── CONFIG ───────────────────────────────────────────
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'service_account.json'

PROJECT_ID = 'fintech-intelligence'   # ← replace with your actual project ID
DATASET_ID = 'fintech_dw'

client = bigquery.Client(project=PROJECT_ID)

def upload_table(df, table_name, schema=None):
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",   # overwrite if exists
        schema=schema,
        autodetect=True if schema is None else False,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print(f"✅ Uploaded {len(df)} rows → {table_id}")

# ── LOAD PROCESSED DATA ──────────────────────────────
master           = pd.read_csv('processed/master_transactions.csv',
                               parse_dates=['date'])
customer_summary = pd.read_csv('processed/customer_summary.csv',
                               parse_dates=['signup_date',
                                            'first_transaction',
                                            'last_transaction'])
customers        = pd.read_csv('processed/customers_clean.csv',
                               parse_dates=['signup_date'])

# ── UPLOAD ───────────────────────────────────────────
print("Uploading to BigQuery...\n")
upload_table(master,           'master_transactions')
upload_table(customer_summary, 'customer_summary')
upload_table(customers,        'customers')

print("\n🎉 All tables loaded into BigQuery successfully!")
print(f"   Project : {PROJECT_ID}")
print(f"   Dataset : {DATASET_ID}")