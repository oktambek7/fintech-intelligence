import pandas as pd
import numpy as np
import os

os.makedirs('processed', exist_ok=True)

# ── LOAD RAW DATA ────────────────────────────────────
customers    = pd.read_csv('raw/customers.csv')
transactions = pd.read_csv('raw/transactions.csv')

print(f"Raw transactions: {len(transactions)}")
print(f"Raw customers:    {len(customers)}")

# ── CLEAN TRANSACTIONS ───────────────────────────────
# Parse dates properly
transactions['date'] = pd.to_datetime(transactions['date'])

# Drop duplicates
transactions.drop_duplicates(subset='transaction_id', inplace=True)

# Drop failed transactions (not useful for analytics)
transactions = transactions[transactions['status'] != 'Failed'].copy()

# Remove negative or zero amounts (data quality)
transactions = transactions[transactions['amount'] > 0].copy()

print(f"After cleaning:   {len(transactions)} transactions")

# ── ENRICH TRANSACTIONS ──────────────────────────────
# Time-based features
transactions['year']    = transactions['date'].dt.year
transactions['month']   = transactions['date'].dt.month
transactions['quarter'] = transactions['date'].dt.quarter
transactions['weekday'] = transactions['date'].dt.day_name()
transactions['hour']    = pd.to_datetime(transactions['time'],
                                          format='%H:%M:%S').dt.hour

# Day part segmentation
def day_part(hour):
    if 6  <= hour < 12: return 'Morning'
    if 12 <= hour < 17: return 'Afternoon'
    if 17 <= hour < 21: return 'Evening'
    return 'Night'

transactions['day_part'] = transactions['hour'].apply(day_part)

# ── ENRICH CUSTOMERS ─────────────────────────────────
customers['signup_date'] = pd.to_datetime(customers['signup_date'])

# Customer age group
def age_group(age):
    if age < 25: return 'Gen Z'
    if age < 40: return 'Millennial'
    if age < 55: return 'Gen X'
    return 'Boomer'

customers['age_group'] = customers['age'].apply(age_group)

# ── BUILD ENRICHED MASTER TABLE ──────────────────────
# Join transactions with customer info
master = transactions.merge(
    customers[['customer_id', 'segment', 'country', 'age_group']],
    on='customer_id',
    how='left'
)

# ── CUSTOMER SUMMARY TABLE ───────────────────────────
customer_summary = transactions.groupby('customer_id').agg(
    total_transactions = ('transaction_id', 'count'),
    total_spent        = ('amount', 'sum'),
    avg_transaction    = ('amount', 'mean'),
    fraud_count        = ('is_fraud', 'sum'),
    first_transaction  = ('date', 'min'),
    last_transaction   = ('date', 'max'),
).reset_index()

customer_summary['total_spent']      = customer_summary['total_spent'].round(2)
customer_summary['avg_transaction']  = customer_summary['avg_transaction'].round(2)

# Merge with customer base
customer_summary = customer_summary.merge(customers, on='customer_id', how='left')

# ── SAVE PROCESSED DATA ──────────────────────────────
master.to_csv('processed/master_transactions.csv', index=False)
customer_summary.to_csv('processed/customer_summary.csv', index=False)
customers.to_csv('processed/customers_clean.csv', index=False)

print("\n✅ Processed files saved:")
print(f"   master_transactions : {len(master)} rows, {master.columns.tolist()}")
print(f"   customer_summary    : {len(customer_summary)} rows")
print(f"\nSample fraud rate by segment:")
print(master.groupby('segment')['is_fraud'].mean().mul(100).round(2).to_string())