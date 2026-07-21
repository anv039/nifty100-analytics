import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "analytics"))

from ratios import debt_to_equity, interest_coverage, net_debt, asset_turnover

def test_de_debtfree():
    de, flag = debt_to_equity(0, 400, 100)
    assert de == 0 and flag is False

def test_de_normal():
    de, flag = debt_to_equity(200, 400, 100)
    assert round(de, 2) == 0.4 and flag is False

def test_de_high_leverage_flag():
    de, flag = debt_to_equity(3000, 400, 100)
    assert flag is True

def test_de_high_leverage_financial_suppressed():
    de, flag = debt_to_equity(3000, 400, 100, is_financial_sector=True)
    assert flag is False

def test_icr_normal():
    icr, label, risk = interest_coverage(500, 50, 100)
    assert icr == 5.5 and label is None and risk is False

def test_icr_debtfree():
    icr, label, risk = interest_coverage(500, 50, 0)
    assert icr is None and label == "Debt Free"

def test_icr_at_risk():
    icr, label, risk = interest_coverage(100, 0, 100)
    assert risk is True

def test_asset_turnover_zero():
    assert asset_turnover(1000, 0) is None