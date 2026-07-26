import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "etl"))
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "nifty100.db")
conn = sqlite3.connect(DB_PATH)

cols = ["net_profit_margin_pct","return_on_equity_pct","debt_to_equity","interest_coverage",
        "revenue_cagr_5yr","pat_cagr_5yr","composite_quality_score"]
for c in cols:
    non_null = conn.execute(f"SELECT COUNT(*) FROM financial_ratios WHERE {c} IS NOT NULL").fetchone()[0]
    print(f"{c}: {non_null} non-null")

print(conn.execute("SELECT company_id, year, return_on_equity_pct, debt_to_equity, composite_quality_score FROM financial_ratios LIMIT 5").fetchall())
conn.close()