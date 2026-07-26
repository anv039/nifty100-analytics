import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "nifty100.db")
conn = sqlite3.connect(DB_PATH)

before = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]

conn.execute("""
    DELETE FROM financial_ratios
    WHERE rowid NOT IN (
        SELECT MAX(rowid) FROM financial_ratios GROUP BY company_id, year
    )
""")
conn.commit()

after = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
print(f"Before: {before}, After: {after}, Removed: {before - after}")
conn.close()