import sqlite3
import os
import random

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nifty100.db")

conn = sqlite3.connect(DB_PATH)
tickers = [r[0] for r in conn.execute("SELECT id FROM companies").fetchall()]
random.seed(42)
sample = random.sample(tickers, 5)
print(f"Sampled: {sample}\n")

for t in sample:
    print(f"=== {t} ===")
    for table in ["profitandloss", "balancesheet", "cashflow"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE company_id=?", (t,)).fetchone()[0]
        years = conn.execute(f"SELECT MIN(year), MAX(year) FROM {table} WHERE company_id=?", (t,)).fetchone()
        print(f"  {table}: {cnt} rows, years {years[0]} to {years[1]}")
    print()

conn.close()