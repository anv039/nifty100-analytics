import sqlite3
import sys
from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "data" / "nifty100.db")
CONFIG_PATH = str(ROOT / "config" / "screener_config.yaml")

def load_latest_ratios():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT f.*, s.broad_sector, p.sales, p.net_profit, p.opm_percentage
        FROM financial_ratios f
        LEFT JOIN sectors s ON f.company_id = s.company_id
        LEFT JOIN profitandloss p ON f.company_id = p.company_id AND f.year = p.year
        WHERE f.year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = f.company_id)
    """, conn)
    conn.close()
    # ICR: Debt Free label treated as infinity
    df["interest_coverage_effective"] = df.apply(
        lambda r: float("inf") if r.get("icr_label") == "Debt Free" else r["interest_coverage"], axis=1)
    return df

def apply_filter(df, column, op, threshold, skip_financials=False):
    if skip_financials and column == "debt_to_equity":
        df = df[(df["broad_sector"] != "Financials") | df[column].isna()]
    if op == "gte":
        return df[df[column] >= threshold]
    elif op == "lte":
        return df[df[column] <= threshold]
    elif op == "eq":
        return df[df[column] == threshold]
    return df

def run_filters(filters: dict):
    """filters: {'roe_min': 15, 'de_max': 1.0, ...} keys must match screener_config.yaml"""
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)["filters"]

    df = load_latest_ratios()
    for key, threshold in filters.items():
        spec = config[key]
        skip_fin = spec["column"] == "debt_to_equity"
        df = apply_filter(df, spec["column"], spec["op"], threshold, skip_financials=skip_fin)

    return df.sort_values("composite_quality_score", ascending=False)

if __name__ == "__main__":
    result = run_filters({"roe_min": 15, "de_max": 1.0})
    print(f"Matched: {len(result)}")
    print(result[["company_id", "return_on_equity_pct", "debt_to_equity"]].head())