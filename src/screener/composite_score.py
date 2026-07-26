import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from engine import load_latest_with_valuation

def winsorize_scale(series, low=10, high=90):
    """Cap at P10/P90, scale to 0-100."""
    p10, p90 = np.nanpercentile(series.dropna(), [low, high]) if series.notna().sum() > 1 else (0, 1)
    clipped = series.clip(p10, p90)
    if p90 == p10:
        return pd.Series(50, index=series.index)
    return (clipped - p10) / (p90 - p10) * 100

def compute_composite(df, sector_relative=False):
    df = df.copy()
    group_col = "broad_sector" if sector_relative else None

    def scale_col(frame, col):
        return winsorize_scale(frame[col]) if col in frame else pd.Series(np.nan, index=frame.index)

    if sector_relative:
        for col in ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                    "revenue_cagr_5yr", "pat_cagr_5yr", "debt_to_equity", "interest_coverage"]:
            df[f"{col}_score"] = df.groupby("broad_sector")[col].transform(
                lambda s: winsorize_scale(s) if s.notna().sum() > 1 else 50)
    else:
        for col in ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                    "revenue_cagr_5yr", "pat_cagr_5yr", "debt_to_equity", "interest_coverage"]:
            df[f"{col}_score"] = scale_col(df, col)

    fcf_positive_score = (df["free_cash_flow_cr"] > 0).astype(float) * 100
    de_score = 100 - df["debt_to_equity_score"]  # lower D/E is better, invert

    df["composite_score_final"] = (
        0.35 * (0.15/0.35 * df["return_on_equity_pct_score"].fillna(0) +
                0.10/0.35 * df["return_on_capital_employed_pct_score"].fillna(0) +
                0.10/0.35 * df["net_profit_margin_pct_score"].fillna(0)) +
        0.30 * (0.15/0.30 * df["revenue_cagr_5yr_score"].fillna(0) * 0 +  # FCF CAGR unavailable, using FCF flag + CFO/PAT proxy
                0.10/0.30 * fcf_positive_score * 0 +
                0.05/0.30 * fcf_positive_score) +
        0.20 * (0.10/0.20 * df["revenue_cagr_5yr_score"].fillna(0) +
                0.10/0.20 * df["pat_cagr_5yr_score"].fillna(0)) +
        0.15 * (0.10/0.15 * de_score.fillna(0) +
                0.05/0.15 * df["interest_coverage_score"].fillna(0))
    )
    return df

if __name__ == "__main__":
    df = load_latest_with_valuation()
    df = compute_composite(df, sector_relative=True)
    print(df[["company_id", "composite_score_final"]].sort_values("composite_score_final", ascending=False).head(10))