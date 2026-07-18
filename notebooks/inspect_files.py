import pandas as pd
import os

folders = ["dataset", "supporting_dataset"]

for folder in folders:
    print(f"\n{'='*60}\n{folder.upper()}\n{'='*60}")
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".xlsx"):
            continue
        path = os.path.join(folder, fname)
        print(f"\n--- {fname} ---")
        xls = pd.ExcelFile(path)
        print(f"Sheets: {xls.sheet_names}")
        for sheet in xls.sheet_names:
            df = pd.read_excel(path, sheet_name=sheet, nrows=5)
            print(f"\n  Sheet: {sheet}")
            print(f"  Shape (first 5 rows shown, use nrows=None for full count): {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Dtypes:\n{df.dtypes}")
            print(f"  Sample:\n{df.head(2)}")