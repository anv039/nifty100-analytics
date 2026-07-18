import pandas as pd, os

CORE = "data/raw"
SUPP = "data/supporting"

def inspect(path, header):
    df = pd.read_excel(path, header=header)
    print(f"\n--- {os.path.basename(path)} ---")
    print(f"Rows: {len(df)}  Cols: {list(df.columns)}")
    print(f"Nulls:\n{df.isnull().sum()[df.isnull().sum()>0]}")
    print(f"Dupes (all cols): {df.duplicated().sum()}")
    if 'company_id' in df.columns:
        print(f"Unique company_id: {df['company_id'].nunique()}")
    for col in df.columns:
        if 'year' in col.lower():
            print(f"Unique {col} formats (sample): {df[col].dropna().unique()[:15]}")

for f in os.listdir(CORE):
    if f.endswith('.xlsx'):
        inspect(os.path.join(CORE, f), header=1)

for f in os.listdir(SUPP):
    if f.endswith('.xlsx'):
        inspect(os.path.join(SUPP, f), header=0)