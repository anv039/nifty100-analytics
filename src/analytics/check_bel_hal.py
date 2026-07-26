import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "nifty100.db")
conn = sqlite3.connect(DB_PATH)

for cid in ["BEL", "HAL"]:
    row = conn.execute("""
        SELECT company_id, year, equity_capital, reserves, total_assets
        FROM balancesheet WHERE company_id=? ORDER BY year DESC LIMIT 3
    """, (cid,)).fetchall()
    print(cid, row)
    pl = conn.execute("""
        SELECT company_id, year, net_profit FROM profitandloss WHERE company_id=? ORDER BY year DESC LIMIT 3
    """, (cid,)).fetchall()
    print(cid, "PL:", pl)

conn.close()