import sqlite3
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parents[2] / "data" / "nifty100.db")
LOG_PATH = str(Path(__file__).resolve().parents[2] / "output" / "ratio_edge_cases.log")

conn = sqlite3.connect(DB_PATH)

fin_companies = [r[0] for r in conn.execute(
    "SELECT company_id FROM sectors WHERE broad_sector='Financials'").fetchall()]
print(f"Financials sector companies: {len(fin_companies)}")

lines = []

# ROE cross-check: computed vs companies.roe_percentage (latest year per company)
rows = conn.execute("""
    SELECT f.company_id, f.year, f.return_on_equity_pct, c.roe_percentage
    FROM financial_ratios f
    JOIN companies c ON f.company_id = c.id
    WHERE f.year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = f.company_id)
""").fetchall()

for cid, year, computed_roe, source_roe in rows:
    if computed_roe is None or source_roe is None:
        continue
    diff = abs(computed_roe - source_roe)
    if diff > 5:
        if abs(computed_roe) > 200:
            category = "formula discrepancy - near-zero equity base"
        elif source_roe < 5:
            category = "data source issue"
        else:
            category = "version difference"
        lines.append(f"[ROE] {cid} {year}: computed={computed_roe:.2f} source={source_roe:.2f} diff={diff:.2f} category={category}")

rows_roce = conn.execute("""
    SELECT f.company_id, f.year, f.return_on_capital_employed_pct, c.roce_percentage
    FROM financial_ratios f
    JOIN companies c ON f.company_id = c.id
    WHERE f.year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = f.company_id)
""").fetchall()

for cid, year, computed_roce, source_roce in rows_roce:
    if computed_roce is None or source_roce is None:
        continue
    diff = abs(computed_roce - source_roce)
    if diff > 5:
        lines.append(f"[ROCE] {cid} {year}: computed={computed_roce:.2f} source={source_roce:.2f} diff={diff:.2f} category=formula discrepancy")

with open(LOG_PATH, "w") as f:
    f.write("\n".join(lines))

print(f"Logged {len(lines)} ROE anomalies to {LOG_PATH}")
conn.close()