def net_profit_margin(net_profit, sales):
    if not sales:
        return None
    return net_profit / sales * 100

def operating_profit_margin(operating_profit, sales, opm_source=None):
    """Returns (computed_opm, mismatch_flag). mismatch_flag True if |diff| > 1%."""
    if not sales:
        return None, False
    computed = operating_profit / sales * 100
    mismatch = opm_source is not None and abs(computed - opm_source) > 1.0
    return computed, mismatch

def return_on_equity(net_profit, equity_capital, reserves):
    equity = (equity_capital or 0) + (reserves or 0)
    if equity <= 0:
        return None
    return net_profit / equity * 100

def return_on_capital_employed(ebit, equity_capital, reserves, borrowings, is_financial_sector=False):
    """is_financial_sector: use sector-relative benchmark instead of absolute threshold downstream."""
    capital_employed = (equity_capital or 0) + (reserves or 0) + (borrowings or 0)
    if capital_employed <= 0:
        return None
    return ebit / capital_employed * 100

def return_on_assets(net_profit, total_assets):
    if not total_assets:
        return None
    return net_profit / total_assets * 100

def debt_to_equity(borrowings, equity_capital, reserves, is_financial_sector=False):
    equity = (equity_capital or 0) + (reserves or 0)
    borrowings = borrowings or 0
    if borrowings == 0:
        return 0, False
    if equity <= 0:
        return None, False
    de = borrowings / equity
    high_leverage_flag = de > 5 and not is_financial_sector
    return de, high_leverage_flag

def interest_coverage(operating_profit, other_income, interest):
    if not interest:
        return None, "Debt Free", False
    icr = (operating_profit + (other_income or 0)) / interest
    at_risk_flag = icr < 1.5
    return icr, None, at_risk_flag

def net_debt(borrowings, investments):
    return (borrowings or 0) - (investments or 0)

def asset_turnover(sales, total_assets):
    if not total_assets:
        return None
    return sales / total_assets