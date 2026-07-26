import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from engine import load_latest_with_valuation

df = load_latest_with_valuation()
print("Non-null sales:", df.sales.notna().sum())
print(df[["company_id", "year", "sales"]].head(10))