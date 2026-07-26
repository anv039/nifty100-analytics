import sqlite3
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = str(ROOT / "data" / "nifty100.db")
OUT_DIR = ROOT / "reports" / "radar_charts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

AXES = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
        "debt_to_equity", "pat_cagr_5yr", "revenue_cagr_5yr"]
LABELS = ["ROE", "ROCE", "NPM", "D/E", "PAT CAGR 5yr", "Rev CAGR 5yr"]

def normalize_row(row, group_df):
    vals = []
    for col in AXES:
        colvals = group_df[col].dropna()
        if len(colvals) < 2 or pd.isna(row[col]):
            vals.append(0)
            continue
        lo, hi = colvals.min(), colvals.max()
        v = 0 if hi == lo else (row[col] - lo) / (hi - lo) * 100
        if col == "debt_to_equity":
            v = 100 - v  # lower D/E is better
        vals.append(v)
    return vals

def plot_radar(company_id, company_vals, group_avg_vals, group_name):
    angles = np.linspace(0, 2*np.pi, len(AXES), endpoint=False).tolist()
    company_vals += company_vals[:1]
    group_avg_vals += group_avg_vals[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True))
    ax.plot(angles, company_vals, 'b-', linewidth=2, label=company_id)
    ax.fill(angles, company_vals, 'b', alpha=0.25)
    ax.plot(angles, group_avg_vals, 'r--', linewidth=1.5, label=f"{group_name} avg")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(LABELS, fontsize=9)
    ax.set_title(company_id, fontsize=12)
    ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.savefig(OUT_DIR / f"{company_id}_radar.png", dpi=100)
    plt.close()

def main():
    conn = sqlite3.connect(DB_PATH)
    peer_groups = pd.read_sql("SELECT peer_group_name, company_id FROM peer_groups", conn)
    ratios = pd.read_sql(f"""
        SELECT company_id, {', '.join(AXES)} FROM financial_ratios
        WHERE year = (SELECT MAX(year) FROM financial_ratios f2 WHERE f2.company_id = financial_ratios.company_id)
    """, conn)
    conn.close()

    merged = peer_groups.merge(ratios, on="company_id", how="inner")
    generated = 0
    for group_name, group_df in merged.groupby("peer_group_name"):
        group_avg_raw = group_df[AXES].mean()
        for _, row in group_df.iterrows():
            company_vals = normalize_row(row, group_df)
            group_avg_vals = normalize_row(group_avg_raw, group_df)
            plot_radar(row["company_id"], company_vals, group_avg_vals, group_name)
            generated += 1

    print(f"Radar charts generated: {generated}")

if __name__ == "__main__":
    main()