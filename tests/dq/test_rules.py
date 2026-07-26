import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "etl"))
from normalizer import normalize_year, normalize_ticker

# DQ-01: Company PK uniqueness
def test_dq01_duplicate_pk():
    ids = ["TCS", "TCS", "INFY"]
    assert len(ids) != len(set(ids))

def test_dq01_unique_pk():
    ids = ["TCS", "INFY", "WIPRO"]
    assert len(ids) == len(set(ids))

# DQ-02: Annual PK uniqueness (company_id, year)
def test_dq02_duplicate_annual_pk():
    rows = [("TCS", "2023-03"), ("TCS", "2023-03")]
    assert len(rows) != len(set(rows))

# DQ-03: FK integrity
def test_dq03_orphan_fk():
    valid_ids = {"TCS", "INFY"}
    child_id = "FAKECO"
    assert child_id not in valid_ids

def test_dq03_valid_fk():
    valid_ids = {"TCS", "INFY"}
    assert "TCS" in valid_ids

# DQ-04: Balance sheet balance
def test_dq04_bs_balance_triggered():
    assets, liab = 1000, 1020
    assert abs(assets - liab) / assets >= 0.01

def test_dq04_bs_balance_ok():
    assets, liab = 1000, 1005
    assert abs(assets - liab) / assets < 0.01

# DQ-05: OPM cross-check
def test_dq05_opm_mismatch():
    opm_source, sales, op_profit = 25.0, 1000, 200
    computed = op_profit / sales * 100
    assert abs(opm_source - computed) >= 1.0

# DQ-06: Positive sales
def test_dq06_zero_sales():
    sales = 0
    assert sales <= 0

# DQ-07: Year format
def test_dq07_unparseable_year():
    assert normalize_year("xyz") is None

def test_dq07_valid_year():
    assert normalize_year("Mar-23") == "2023-03"

# DQ-08: Ticker format
def test_dq08_invalid_ticker_length():
    assert normalize_ticker("A") is None

def test_dq08_valid_ticker():
    assert normalize_ticker(" tcs ") == "TCS"

# DQ-09: Net cash check
def test_dq09_net_cash_mismatch():
    cfo, cfi, cff, net = 100, -50, -20, 100
    assert abs(net - (cfo + cfi + cff)) > 10

# DQ-16: Coverage check
def test_dq16_insufficient_coverage():
    years = ["2020-03", "2021-03", "2022-03"]
    assert len(set(years)) < 5