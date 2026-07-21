import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "analytics"))

from ratios import net_profit_margin, operating_profit_margin, return_on_equity, return_on_capital_employed, return_on_assets

def test_npm_normal(): assert net_profit_margin(100, 1000) == 10.0
def test_npm_zero_sales(): assert net_profit_margin(100, 0) is None

def test_opm_normal():
    computed, mismatch = operating_profit_margin(200, 1000, opm_source=20.0)
    assert computed == 20.0 and mismatch is False

def test_opm_mismatch():
    computed, mismatch = operating_profit_margin(200, 1000, opm_source=15.0)
    assert mismatch is True

def test_opm_zero_sales():
    computed, mismatch = operating_profit_margin(200, 0)
    assert computed is None

def test_roe_normal(): assert return_on_equity(100, 400, 100) == 20.0
def test_roe_negative_equity(): assert return_on_equity(100, -400, 100) is None

def test_roa_normal(): assert return_on_assets(100, 1000) == 10.0