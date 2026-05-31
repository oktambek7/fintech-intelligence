import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import os

os.makedirs('raw', exist_ok=True)
os.makedirs('processed', exist_ok=True)

fake = Faker()
np.random.seed(42)
random.seed(42)

# ── CONFIG ──────────────────────────────────────────
N_CUSTOMERS = 1_000
N_TRANSACTIONS = 50_000
START_DATE = datetime(2023, 1, 1)
END_DATE   = datetime(2024, 12, 31)

# ── CUSTOMERS ────────────────────────────────────────
segments = ['Premium', 'Standard', 'Basic']
seg_weights = [0.15, 0.50, 0.35]

customers = pd.DataFrame({
    'customer_id':  [f'C{str(i).zfill(5)}' for i in range(1, N_CUSTOMERS + 1)],
    'name':         [fake.name() for _ in range(N_CUSTOMERS)],
    'age':          np.random.randint(18, 72, N_CUSTOMERS),
    'country':      np.random.choice(['UZ', 'KZ', 'RU', 'TR', 'AE'], N_CUSTOMERS,
                                     p=[0.50, 0.20, 0.15, 0.10, 0.05]),
    'segment':      np.random.choice(segments, N_CUSTOMERS, p=seg_weights),
    'signup_date':  [fake.date_between(start_date='-4y', end_date='-1y')
                     for _ in range(N_CUSTOMERS)],
})

# ── TRANSACTIONS ─────────────────────────────────────
categories   = ['Transfer', 'Payment', 'Withdrawal', 'Deposit', 'Refund']
cat_weights  = [0.30, 0.35, 0.15, 0.15, 0.05]
channels     = ['Mobile', 'Web', 'ATM', 'Branch']
chan_weights  = [0.55, 0.25, 0.15, 0.05]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_amount(segment, category):
    base = {'Premium': 800, 'Standard': 250, 'Basic': 80}[segment]
    if category == 'Deposit':
        return round(abs(np.random.normal(base * 3, base)), 2)
    if category == 'Withdrawal':
        return round(abs(np.random.normal(base * 0.8, base * 0.3)), 2)
    return round(abs(np.random.normal(base, base * 0.5)), 2)

cust_ids   = customers['customer_id'].tolist()
cust_segs  = dict(zip(customers['customer_id'], customers['segment']))

rows = []
for i in range(1, N_TRANSACTIONS + 1):
    cid      = random.choice(cust_ids)
    cat      = np.random.choice(categories, p=cat_weights)
    chan     = np.random.choice(channels,   p=chan_weights)
    txn_date = random_date(START_DATE, END_DATE)
    amount   = generate_amount(cust_segs[cid], cat)

    # inject ~2% fraud: late night + unusual amount
    is_fraud = (
        txn_date.hour in range(1, 5)
        and amount > 1500
        and random.random() < 0.35
    )

    rows.append({
        'transaction_id': f'T{str(i).zfill(7)}',
        'customer_id':    cid,
        'date':           txn_date.date(),
        'time':           txn_date.strftime('%H:%M:%S'),
        'category':       cat,
        'channel':        chan,
        'amount':         amount,
        'currency':       'USD',
        'is_fraud':       int(is_fraud),
        'status':         np.random.choice(['Completed', 'Pending', 'Failed'],
                                           p=[0.92, 0.05, 0.03]),
    })

transactions = pd.DataFrame(rows)

# ── SAVE ─────────────────────────────────────────────
customers.to_csv('raw/customers.csv', index=False)
transactions.to_csv('raw/transactions.csv', index=False)

print(f"✅ {len(customers)} customers saved to raw/customers.csv")
print(f"✅ {len(transactions)} transactions saved to raw/transactions.csv")
print(f"\nFraud transactions: {transactions['is_fraud'].sum()} "
      f"({transactions['is_fraud'].mean()*100:.1f}%)")
print(f"Date range: {transactions['date'].min()} → {transactions['date'].max()}")