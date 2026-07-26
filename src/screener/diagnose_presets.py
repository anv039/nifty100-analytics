import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from engine import load_latest_with_valuation

df = load_latest_with_valuation()
print("Total companies:", len(df))
print("Non-null pe_ratio:", df.pe_ratio.notna().sum())
print("Non-null pb_ratio:", df.pb_ratio.notna().sum())
print("Non-null dividend_yield_pct:", df.dividend_yield_pct.notna().sum())
print("Non-null dividend_payout:", df.dividend_payout.notna().sum())
print("debt_to_equity == 0 count:", (df.debt_to_equity == 0).sum())
print("sales > 5000 count:", (df.sales > 5000).sum())
print("dividend_yield_pct > 2 count:", (df.dividend_yield_pct > 2).sum())