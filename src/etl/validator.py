import os
import re
import pandas as pd
from loader import load_all
from normalizer import normalize_year, normalize_ticker

FAILURES = []

def log(rule_id, severity, table, company_id, year, field, issue):
    FAILURES.append({
        "rule_id": rule_id, "severity": severity, "table": table,
        "company_id": company_id, "year": year, "field": field, "issue": issue
    })

def apply_normalization(tables):
    """Normalize company_id and year columns in place before validation."""
    for name, df in tables.items():
        id_col = "company_id" if "company_id" in df.columns else ("id" if name == "companies" else None)
        if name == "companies":
            df["id"] = df["id"].apply(normalize_ticker)
        elif "company_id" in df.columns:
            df["company_id"] = df["company_id"].apply(normalize_ticker)

        year_col = "year" if "year" in df.columns else ("Year" if "Year" in df.columns else None)
        if year_col:
            df["_year_norm"] = df[year_col].apply(normalize_year)
    return tables

def dq01_company_pk(tables):
    df = tables["companies"]
    if len(df) != df["id"].nunique():
        dupes = df[df["id"].duplicated(keep=False)]["id"].unique()
        for tid in dupes:
            log("DQ-01", "CRITICAL", "companies", tid, None, "id", "Duplicate company PK")

def dq02_annual_pk(tables):
    for name in ["profitandloss", "balancesheet", "cashflow"]:
        df = tables[name]
        dupe_mask = df.duplicated(subset=["company_id", "_year_norm"], keep="last")
        for _, row in df[dupe_mask].iterrows():
            log("DQ-02", "CRITICAL", name, row["company_id"], row["_year_norm"], "company_id+year", "Duplicate annual PK, keeping last")
        tables[name] = df[~dupe_mask]

def dq03_fk_integrity(tables):
    valid_ids = set(tables["companies"]["id"])
    for name, df in tables.items():
        if name == "companies" or "company_id" not in df.columns:
            continue
        orphan_mask = ~df["company_id"].isin(valid_ids)
        for _, row in df[orphan_mask].iterrows():
            log("DQ-03", "CRITICAL", name, row["company_id"], row.get("_year_norm"), "company_id", "Orphan row - no matching company")
        tables[name] = df[~orphan_mask]

def dq04_bs_balance(tables):
    df = tables["balancesheet"]
    for _, row in df.iterrows():
        ta = row["total_assets"]
        tl = row["total_liabilities"]
        if ta and abs(ta - tl) / ta >= 0.01:
            log("DQ-04", "WARNING", "balancesheet", row["company_id"], row["_year_norm"], "total_assets/total_liabilities", f"Mismatch: {ta} vs {tl}")

def dq05_opm_crosscheck(tables):
    df = tables["profitandloss"]
    for _, row in df.iterrows():
        sales, op, opm = row.get("sales"), row.get("operating_profit"), row.get("opm_percentage")
        if pd.isna(op) or pd.isna(opm) or not sales:
            continue
        computed = op / sales * 100
        if abs(opm - computed) >= 1.0:
            log("DQ-05", "WARNING", "profitandloss", row["company_id"], row["_year_norm"], "opm_percentage", f"Source {opm} vs computed {computed:.2f}")

def dq06_positive_sales(tables):
    df = tables["profitandloss"]
    for _, row in df[df["sales"] <= 0].iterrows():
        log("DQ-06", "WARNING", "profitandloss", row["company_id"], row["_year_norm"], "sales", f"Non-positive sales: {row['sales']}")

def dq07_year_format(tables):
    for name in ["profitandloss", "balancesheet", "cashflow"]:
        df = tables[name]
        bad_mask = df["_year_norm"].apply(lambda y: y is None or not re.match(r"^\d{4}-\d{2}$", str(y)))
        for _, row in df[bad_mask].iterrows():
            year_col = "year"
            log("DQ-07", "CRITICAL", name, row["company_id"], row.get(year_col), "year", f"Unparseable year: {row.get(year_col)}")
        tables[name] = df[~bad_mask]

def dq08_ticker_format(tables):
    for name, df in tables.items():
        col = "id" if name == "companies" else ("company_id" if "company_id" in df.columns else None)
        if not col:
            continue
        bad_mask = df[col].isna()
        for _, row in df[bad_mask].iterrows():
            log("DQ-08", "CRITICAL", name, None, row.get("_year_norm"), col, "Invalid ticker format/length")
        tables[name] = df[~bad_mask]

def dq09_net_cash_check(tables):
    df = tables["cashflow"]
    for _, row in df.iterrows():
        cfo, cfi, cff, net = row.get("operating_activity"), row.get("investing_activity"), row.get("financing_activity"), row.get("net_cash_flow")
        if pd.isna(cfo) or pd.isna(cfi) or pd.isna(cff) or pd.isna(net):
            continue
        if abs(net - (cfo + cfi + cff)) > 10:
            log("DQ-09", "WARNING", "cashflow", row["company_id"], row["_year_norm"], "net_cash_flow", "Mismatch vs CFO+CFI+CFF beyond ±10 Cr")

def dq10_nonneg_fixed_assets(tables):
    df = tables["balancesheet"]
    neg_mask = df["fixed_assets"] < 0
    for idx, row in df[neg_mask].iterrows():
        log("DQ-10", "WARNING", "balancesheet", row["company_id"], row["_year_norm"], "fixed_assets", f"Negative value {row['fixed_assets']} coerced to 0")
    tables["balancesheet"].loc[neg_mask, "fixed_assets"] = 0

def dq11_tax_rate_range(tables):
    df = tables["profitandloss"]
    bad = df[(df["tax_percentage"] < 0) | (df["tax_percentage"] > 60)]
    for _, row in bad.iterrows():
        log("DQ-11", "WARNING", "profitandloss", row["company_id"], row["_year_norm"], "tax_percentage", f"Out of range: {row['tax_percentage']}")

def dq12_dividend_payout_cap(tables):
    df = tables["profitandloss"]
    bad = df[df["dividend_payout"] > 200]
    for _, row in bad.iterrows():
        log("DQ-12", "WARNING", "profitandloss", row["company_id"], row["_year_norm"], "dividend_payout", f">200%: {row['dividend_payout']}")

def dq14_eps_sign(tables):
    df = tables["profitandloss"]
    bad = df[(df["net_profit"] > 0) & (df["eps"] <= 0)]
    for _, row in bad.iterrows():
        log("DQ-14", "WARNING", "profitandloss", row["company_id"], row["_year_norm"], "eps", f"eps={row['eps']} but net_profit>0")

def dq16_coverage_check(tables):
    for name in ["profitandloss", "balancesheet", "cashflow"]:
        df = tables[name]
        counts = df.groupby("company_id")["_year_norm"].nunique()
        for cid, cnt in counts[counts < 5].items():
            log("DQ-16", "WARNING", name, cid, None, "coverage", f"Only {cnt} years of history")

def run_validation():
    tables = load_all()
    tables = apply_normalization(tables)

    dq01_company_pk(tables)
    dq02_annual_pk(tables)
    dq03_fk_integrity(tables)
    dq04_bs_balance(tables)
    dq05_opm_crosscheck(tables)
    dq06_positive_sales(tables)
    dq07_year_format(tables)
    dq08_ticker_format(tables)
    dq09_net_cash_check(tables)
    dq10_nonneg_fixed_assets(tables)
    dq11_tax_rate_range(tables)
    dq12_dividend_payout_cap(tables)
    dq14_eps_sign(tables)
    dq16_coverage_check(tables)

    os.makedirs("output", exist_ok=True)
    pd.DataFrame(FAILURES).to_csv("output/validation_failures.csv", index=False)
    print(f"Total failures logged: {len(FAILURES)}")
    print(pd.DataFrame(FAILURES)["rule_id"].value_counts() if FAILURES else "No failures")
    return tables

if __name__ == "__main__":
    run_validation()