def free_cash_flow(operating_activity, investing_activity):
    return (operating_activity or 0) + (investing_activity or 0)

def cfo_quality_score(cfo_values, pat_values):
    """cfo_values, pat_values: lists of up to 5 years. Returns (ratio, label)."""
    pairs = [(c, p) for c, p in zip(cfo_values, pat_values) if p]
    if not pairs:
        return None, None
    avg_ratio = sum(c / p for c, p in pairs) / len(pairs)
    if avg_ratio > 1.0:
        label = "High Quality"
    elif avg_ratio >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
    return avg_ratio, label

def capex_intensity(investing_activity, sales):
    if not sales:
        return None, None
    pct = abs(investing_activity) / sales * 100
    if pct < 3:
        label = "Asset Light"
    elif pct <= 8:
        label = "Moderate"
    else:
        label = "Capital Intensive"
    return pct, label

def fcf_conversion_rate(fcf, operating_profit):
    if not operating_profit:
        return None
    return fcf / operating_profit * 100

def capital_allocation_pattern(cfo, cfi, cff, cfo_pat_ratio=None):
    cfo_sign = "+" if cfo > 0 else "-"
    cfi_sign = "+" if cfi > 0 else "-"
    cff_sign = "+" if cff > 0 else "-"
    pattern = (cfo_sign, cfi_sign, cff_sign)

    if pattern == ("+", "-", "-"):
        label = "Shareholder Returns" if cfo_pat_ratio and cfo_pat_ratio > 1.0 else "Reinvestor"
    elif pattern == ("+", "+", "-"):
        label = "Liquidating Assets"
    elif pattern == ("-", "+", "+"):
        label = "Distress Signal"
    elif pattern == ("-", "-", "+"):
        label = "Growth Funded by Debt"
    elif pattern == ("+", "+", "+"):
        label = "Cash Accumulator"
    elif pattern == ("-", "-", "-"):
        label = "Pre-Revenue"
    elif pattern == ("+", "-", "+"):
        label = "Mixed"
    else:
        label = "Uncategorized"

    return cfo_sign, cfi_sign, cff_sign, label