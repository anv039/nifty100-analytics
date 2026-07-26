import sqlite3
import os
from validator import run_validation

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nifty100.db")

def build_database():
    tables = run_validation()  # returns cleaned tables post-DQ

    os.makedirs("data", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())

    rename_map = {
        "profitandloss": {"id": "row_id", "_year_norm": "year"},
        "balancesheet": {"id": "row_id", "_year_norm": "year"},
        "cashflow": {"id": "row_id", "_year_norm": "year"},
    }

    for name, df in tables.items():
        df = df.copy()
        if name == "documents":
            df = df.rename(columns={"Year": "year", "Annual_Report": "annual_report"})
        if name in rename_map:
            df = df.drop(columns=["year"]).rename(columns={"_year_norm": "year", "id": "row_id"})
        elif "_year_norm" in df.columns:
            df = df.drop(columns=["_year_norm"])
        df.to_sql(name, conn, if_exists="append", index=False)

    fk_check = conn.execute("PRAGMA foreign_key_check;").fetchall()
    print(f"FK check violations: {len(fk_check)}")

    for table in ["companies", "profitandloss", "balancesheet", "cashflow", "analysis",
                  "documents", "prosandcons", "sectors", "stock_prices", "market_cap",
                  "financial_ratios", "peer_groups"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {cnt} rows")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_database()