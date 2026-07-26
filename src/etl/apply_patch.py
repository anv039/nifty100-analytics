import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "data" / "nifty100.db")
PATCH_SQL = str(ROOT / "src" / "etl" / "add_ratio_columns.sql")

conn = sqlite3.connect(DB_PATH)
with open(PATCH_SQL) as f:
    for stmt in f.read().split(";"):
        stmt = stmt.strip()
        if not stmt:
            continue
        try:
            conn.execute(stmt)
            print(f"OK: {stmt[:60]}")
        except sqlite3.OperationalError as e:
            print(f"SKIP ({e}): {stmt[:60]}")
conn.commit()
conn.close()