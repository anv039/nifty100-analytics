import pandas as pd
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nifty100.db")
RAW_COUNTS = {
    "companies": 92, "profitandloss": 1276, "balancesheet": 1312, "cashflow": 1187,
    "analysis": 20, "documents": 1585, "prosandcons": 16, "sectors": 92,
    "stock_prices": 5520, "market_cap": 552, "financial_ratios": 1184, "peer_groups": 56
}

conn = sqlite3.connect(DB_PATH)
rows = []
for table, raw_count in RAW_COUNTS.items():
    loaded = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    rows.append({"table": table, "rows_in": raw_count, "rows_out": loaded, "rejected": raw_count - loaded})
conn.close()

pd.DataFrame(rows).to_csv("output/load_audit.csv", index=False)
print(pd.DataFrame(rows))