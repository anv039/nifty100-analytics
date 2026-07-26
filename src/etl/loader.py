import os
import pandas as pd

CORE_FILES = {
    "companies": "companies.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "documents": "documents.xlsx",
    "prosandcons": "prosandcons.xlsx",
}

SUPP_FILES = {
    "sectors": "sectors.xlsx",
    "stock_prices": "stock_prices.xlsx",
    "market_cap": "market_cap.xlsx",
    "financial_ratios": "financial_ratios.xlsx",
    "peer_groups": "peer_groups.xlsx",
}

def load_core(data_dir="data/raw") -> dict[str, pd.DataFrame]:
    """Load 7 core files with header=1 (row 0 is title junk)."""
    return {
        name: pd.read_excel(os.path.join(data_dir, fname), header=1)
        for name, fname in CORE_FILES.items()
    }

def load_supporting(data_dir="data/supporting") -> dict[str, pd.DataFrame]:
    """Load 5 supplementary files with header=0 (already clean)."""
    return {
        name: pd.read_excel(os.path.join(data_dir, fname), header=0)
        for name, fname in SUPP_FILES.items()
    }

def load_all() -> dict[str, pd.DataFrame]:
    tables = {}
    tables.update(load_core())
    tables.update(load_supporting())
    return tables

if __name__ == "__main__":
    tables = load_all()
    for name, df in tables.items():
        print(f"{name}: {df.shape}")