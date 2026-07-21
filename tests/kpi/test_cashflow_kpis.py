import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "analytics"))

from cashflow_kpis import free_cash_flow, cfo_quality_score, capex_intensity, fcf_conversion_rate, capital_allocation_pattern

def test_fcf_normal():
    assert free_cash_flow(500, -200) == 300

def test_cfo_quality_high():
    ratio, label = cfo_quality_score([600]*5, [500]*5)
    assert label == "High Quality"

def test_cfo_quality_accrual_risk():
    ratio, label = cfo_quality_score([100]*5, [500]*5)
    assert label == "Accrual Risk"

def test_capex_asset_light():
    pct, label = capex_intensity(-20, 1000)
    assert label == "Asset Light"

def test_capex_capital_intensive():
    pct, label = capex_intensity(-100, 1000)
    assert label == "Capital Intensive"

def test_fcf_conversion_zero_opprofit():
    assert fcf_conversion_rate(300, 0) is None

def test_pattern_reinvestor():
    _, _, _, label = capital_allocation_pattern(500, -200, -100)
    assert label == "Reinvestor"

def test_pattern_distress():
    _, _, _, label = capital_allocation_pattern(-100, 200, 300)
    assert label == "Distress Signal"