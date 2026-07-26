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

PRESETS = {
    "Quality Compounder": {"roe_min": 15, "de_max": 1.0, "fcf_min": 0.01, "revenue_cagr_5yr_min": 10},
    "Value Pick": {"de_max": 2.0},  # P/E, P/B, Div Yield need market_cap join - added below
    "Growth Accelerator": {"pat_cagr_5yr_min": 20, "revenue_cagr_5yr_min": 15, "de_max": 2.0},
    "Dividend Champion": {"fcf_min": 0.01},  # Div Yield/Payout need market_cap/PL join - added below
    "Debt-Free Blue Chip": {"de_max": 0, "roe_min": 12, "sales_min": 5000},
    "Turnaround Watch": {"revenue_cagr_5yr_min": 0},  # simplified proxy, see note
}

def load_latest_with_valuation():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT f.*, s.broad_sector, m.pe_ratio, m.pb_ratio, m.dividend_yield_pct
        FROM financial_ratios f
        LEFT JOIN sectors s ON f.company_id = s.company_id
        LEFT JOIN market_cap m ON f.company_id = m.company_id
            AND m.year = (SELECT MAX(year) FROM market_cap m2 WHERE m2.company_id = f.company_id)
        WHERE f.year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = f.company_id)
    """, conn)

    sys.path.insert(0, str(ROOT / "src" / "etl"))
    from normalizer import normalize_year
    df["year_norm"] = df["year"].apply(normalize_year)

    pl = pd.read_sql("SELECT company_id, year, sales, net_profit, dividend_payout FROM profitandloss", conn)
    conn.close()

    df = df.merge(pl, left_on=["company_id", "year_norm"], right_on=["company_id", "year"],
                   how="left", suffixes=("", "_pl"))
    return df

def run_preset(name):
    df = load_latest_with_valuation()

    if name == "Quality Compounder":
        return df[(df.return_on_equity_pct > 15) & (df.debt_to_equity < 1.0) &
                   (df.free_cash_flow_cr > 0) & (df.revenue_cagr_5yr > 10)]
    elif name == "Value Pick":
        return df[(df.pe_ratio < 20) & (df.pb_ratio < 3.0) & (df.debt_to_equity < 2.0) & (df.dividend_yield_pct > 1)]
    elif name == "Growth Accelerator":
        return df[(df.pat_cagr_5yr > 20) & (df.revenue_cagr_5yr > 15) & (df.debt_to_equity < 2.0)]
    elif name == "Dividend Champion":
        return df[(df.dividend_yield_pct > 2) & (df.dividend_payout < 80) & (df.free_cash_flow_cr > 0)]
    elif name == "Debt-Free Blue Chip":
        return df[(df.debt_to_equity == 0) & (df.return_on_equity_pct > 12) & (df.sales > 5000)]
    elif name == "Turnaround Watch":
        # Revenue CAGR 3yr not yet computed (only 5yr exists) - using 5yr as proxy, flagged
        return df[(df.revenue_cagr_5yr > 10) & (df.free_cash_flow_cr > 0)]
    return df

if __name__ == "__main__":
    result = run_filters({"roe_min": 15, "de_max": 1.0})
    print(f"Matched: {len(result)}")
    print(result[["company_id", "return_on_equity_pct", "debt_to_equity"]].head())