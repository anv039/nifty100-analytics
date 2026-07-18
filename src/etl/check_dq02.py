from loader import load_all
from normalizer import normalize_year, normalize_ticker

tables = load_all()
df = tables["profitandloss"].copy()
df["company_id"] = df["company_id"].apply(normalize_ticker)
df["_year_norm"] = df["year"].apply(normalize_year)

dupes = df[df.duplicated(subset=["company_id", "_year_norm"], keep=False)]
print(f"Total duplicate rows: {len(dupes)}")
print(dupes.sort_values(["company_id", "_year_norm"])[["company_id", "year", "_year_norm"]].head(20))