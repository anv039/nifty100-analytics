import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "nifty100.db")
conn = sqlite3.connect(DB_PATH)

rows = conn.execute("""
    SELECT company_id, return_on_equity_pct, debt_to_equity
    FROM financial_ratios
    WHERE year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = financial_ratios.company_id)
    AND return_on_equity_pct > 15 AND debt_to_equity < 1
""").fetchall()

print(f"Companies matching ROE>15% AND D/E<1: {len(rows)}")
for r in rows:
    print(r)
conn.close()