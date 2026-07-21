import re
import pandas as pd

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "march": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08", "sep": "09",
    "oct": "10", "nov": "11", "dec": "12",
}

def normalize_year(raw) -> str | None:
    """Convert varied year labels to 'YYYY-MM'. Returns None if unparseable (PARSE_ERROR)."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    s = str(raw).strip()

    if s.upper() == "TTM":
        return None

    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        return s

    # FY23, FY2023 — check BEFORE generic month pattern
    m = re.match(r"^FY(\d{2,4})$", s, re.IGNORECASE)
    if m:
        yr = int(m.group(1))
        yr = yr + 2000 if yr < 100 else yr
        return f"{yr}-03"

    # Mar-23, Mar 23, March-2023, Dec 2012
    m = re.match(r"^([A-Za-z]+)[\s\-]?(\d{2,4})$", s)
    if m:
        mon_raw, yr_raw = m.group(1).lower(), m.group(2)
        mon = MONTH_MAP.get(mon_raw)
        if mon is None:
            return None
        yr = int(yr_raw)
        yr = yr + 2000 if yr < 100 else yr
        return f"{yr}-{mon}"

    m = re.match(r"^(\d{4})$", s)
    if m:
        return f"{m.group(1)}-03"

    return None

def normalize_ticker(raw) -> str | None:
    """Strip whitespace, uppercase. Reject if length not in 2-12 (DQ-08)."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    s = str(raw).strip().upper()
    if not (2 <= len(s) <= 12):
        return None
    return s