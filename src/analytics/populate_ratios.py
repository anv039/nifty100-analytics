import sqlite3
import os
import sys
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "analytics"))
sys.path.insert(0, str(ROOT / "src" / "etl"))

from ratios import return_on_equity, debt_to_equity, interest_coverage, asset_turnover, return_on_capital_employed
from cagr import compute_cagr
from cashflow_kpis import free_cash_flow, capital_allocation_pattern
from normalizer import normalize_year

DB_PATH = str(ROOT / "data" / "nifty100.db")
PATCH_SQL = str(ROOT / "src" / "etl" / "add_ratio_columns.sql")

def get_company_series(conn, table, company_id):
    rows = conn.execute(f"SELECT * FROM {table} WHERE company_id=? ORDER BY year", (company_id,)).fetchall()
    cols = [d[0] for d in conn.execute(f"SELECT * FROM {table} LIMIT 1").description]
    return [dict(zip(cols, r)) for r in rows]

def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        with open(PATCH_SQL) as f:
            conn.executescript(f.read())
    except sqlite3.OperationalError:
        pass

    financial_sectors = {r[0] for r in conn.execute(
        "SELECT company_id FROM sectors WHERE broad_sector='Financials'").fetchall()}
    fr_rows = conn.execute("SELECT rowid, company_id, year FROM financial_ratios").fetchall()

    fr_lookup = {}
    for rowid, cid_raw, yr_raw in fr_rows:
        key = (cid_raw, normalize_year(yr_raw))
        fr_lookup.setdefault(key, []).append(rowid)

    companies = [r[0] for r in conn.execute("SELECT id FROM companies").fetchall()]
    capital_rows = []

    for cid in companies:
        pl = get_company_series(conn, "profitandloss", cid)
        bs = get_company_series(conn, "balancesheet", cid)
        cf = get_company_series(conn, "cashflow", cid)
        bs_by_year = {r["year"]: r for r in bs}
        cf_by_year = {r["year"]: r for r in cf}
        is_fin = cid in financial_sectors

        for i, row in enumerate(pl):
            year = row["year"]
            bsr = bs_by_year.get(year)
            cfr = cf_by_year.get(year)
            if not bsr:
                continue

            roe = return_on_equity(row["net_profit"], bsr["equity_capital"], bsr["reserves"])
            ebit = (row["operating_profit"] or 0) - (row["depreciation"] or 0)
            roce = return_on_capital_employed(ebit, bsr["equity_capital"], bsr["reserves"], bsr["borrowings"], is_fin)
            de, high_lev_flag = debt_to_equity(bsr["borrowings"], bsr["equity_capital"], bsr["reserves"], is_fin)
            if row["operating_profit"] is not None and row["interest"] is not None:
                icr, icr_label, _ = interest_coverage(row["operating_profit"], row["other_income"], row["interest"])
            else:
                icr, icr_label = None, None
            at = asset_turnover(row["sales"], bsr["total_assets"])

            fcf = None
            if cfr and cfr["operating_activity"] is not None and cfr["investing_activity"] is not None and cfr["financing_activity"] is not None:
                fcf = free_cash_flow(cfr["operating_activity"], cfr["investing_activity"])
                cfo_sign, cfi_sign, cff_sign, pattern_label = capital_allocation_pattern(
                    cfr["operating_activity"], cfr["investing_activity"], cfr["financing_activity"])
                capital_rows.append((cid, year, cfo_sign, cfi_sign, cff_sign, pattern_label))

            rev_cagr, rev_flag, pat_cagr, pat_flag, eps_cagr, eps_flag = (None,)*6
            if i >= 5:
                base = pl[i-5]
                n = 5
                rev_cagr, rev_flag = compute_cagr(base["sales"], row["sales"], n)
                pat_cagr, pat_flag = compute_cagr(base["net_profit"], row["net_profit"], n)
                if base["eps"] and row["eps"] is not None:
                    eps_cagr, eps_flag = compute_cagr(base["eps"], row["eps"], n)

            roe_score = min(max((roe or 0), 0), 30) / 30 * 100
            fcf_score = 100 if (fcf or 0) > 0 else 0
            de_score = 100 if de == 0 else max(0, 100 - de * 20)
            composite = 0.3*roe_score + 0.25*fcf_score + 0.25*roe_score + 0.20*de_score

            target_rowids = fr_lookup.get((cid, year), [])
            for rowid in target_rowids:
                conn.execute("""
                    UPDATE financial_ratios SET
                        return_on_equity_pct=?, return_on_capital_employed_pct=?, debt_to_equity=?, interest_coverage=?, asset_turnover=?,
                        free_cash_flow_cr=?, revenue_cagr_5yr=?, revenue_cagr_5yr_flag=?,
                        pat_cagr_5yr=?, pat_cagr_5yr_flag=?, eps_cagr_5yr=?, eps_cagr_5yr_flag=?,
                        composite_quality_score=?, icr_label=?, high_leverage_flag=?
                    WHERE rowid=?
                """, (roe, roce, de, icr, at, fcf, rev_cagr, rev_flag, pat_cagr, pat_flag,
                      eps_cagr, eps_flag, composite, icr_label, int(high_lev_flag), rowid))

    conn.commit()

    os.makedirs(str(ROOT / "output"), exist_ok=True)
    with open(str(ROOT / "output" / "capital_allocation.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"])
        writer.writerows(capital_rows)

    cnt = conn.execute("SELECT COUNT(*) FROM financial_ratios").fetchone()[0]
    print(f"financial_ratios rows: {cnt}")
    print(f"capital_allocation.csv rows: {len(capital_rows)}")
    conn.close()

if __name__ == "__main__":
    main()