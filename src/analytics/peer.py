import sqlite3
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "data" / "nifty100.db")
sys.path.insert(0, str(ROOT / "src" / "etl"))
from normalizer import normalize_year

METRICS = [
    "return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
    "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr",
    "eps_cagr_5yr", "interest_coverage", "asset_turnover"
]
INVERT_METRICS = {"debt_to_equity"}  # lower is better

def load_peer_data():
    conn = sqlite3.connect(DB_PATH)
    peer_groups = pd.read_sql("SELECT peer_group_name, company_id FROM peer_groups", conn)
    ratios = pd.read_sql(f"""
        SELECT company_id, year, {', '.join(METRICS)}
        FROM financial_ratios
        WHERE year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = financial_ratios.company_id)
    """, conn)
    conn.close()
    return peer_groups, ratios

def compute_percentiles():
    peer_groups, ratios = load_peer_data()
    merged = peer_groups.merge(ratios, on="company_id", how="left")

    rows = []
    for group_name, group_df in merged.groupby("peer_group_name"):
        for metric in METRICS:
            valid = group_df[group_df[metric].notna()]
            if len(valid) < 2:
                continue
            pct = valid[metric].rank(pct=True)
            if metric in INVERT_METRICS:
                pct = 1 - pct
            for cid, year, val, p in zip(valid["company_id"], valid["year"], valid[metric], pct):
                rows.append({"company_id": cid, "peer_group_name": group_name, "metric": metric,
                             "value": val, "percentile_rank": p, "year": year})

    result = pd.DataFrame(rows)

    no_group = set(ratios["company_id"]) - set(peer_groups["company_id"])
    print(f"Companies with no peer group ({len(no_group)}): No peer group assigned")

    return result

def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS peer_percentiles")
    df.to_sql("peer_percentiles", conn, index=False)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    df = compute_percentiles()
    save_to_db(df)
    print(f"peer_percentiles rows: {len(df)}")
    print(df.head(10))