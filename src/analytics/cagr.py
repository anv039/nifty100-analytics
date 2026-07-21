def compute_cagr(start_value, end_value, n_years):
    """Returns (cagr_pct, flag). flag is None if computed normally, else edge-case label."""
    if n_years is None or n_years < 3:
        return None, "INSUFFICIENT"
    if start_value == 0:
        return None, "ZERO_BASE"
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"
    cagr = ((end_value / start_value) ** (1 / n_years) - 1) * 100
    return cagr, None