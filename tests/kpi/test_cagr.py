import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "analytics"))

from cagr import compute_cagr

def test_cagr_normal():
    cagr, flag = compute_cagr(100, 161.05, 5)
    assert flag is None and round(cagr, 1) == 10.0

def test_cagr_turnaround():
    cagr, flag = compute_cagr(-100, 200, 5)
    assert cagr is None and flag == "TURNAROUND"

def test_cagr_decline_to_loss():
    cagr, flag = compute_cagr(100, -50, 5)
    assert cagr is None and flag == "DECLINE_TO_LOSS"

def test_cagr_both_negative():
    cagr, flag = compute_cagr(-100, -50, 5)
    assert cagr is None and flag == "BOTH_NEGATIVE"

def test_cagr_zero_base():
    cagr, flag = compute_cagr(0, 100, 5)
    assert cagr is None and flag == "ZERO_BASE"

def test_cagr_insufficient():
    cagr, flag = compute_cagr(100, 150, 2)
    assert cagr is None and flag == "INSUFFICIENT"

def test_cagr_3yr_window():
    cagr, flag = compute_cagr(100, 133.1, 3)
    assert flag is None and round(cagr, 1) == 10.0

def test_cagr_10yr_window():
    cagr, flag = compute_cagr(100, 259.4, 10)
    assert flag is None and round(cagr, 1) == 10.0

def test_cagr_negative_growth():
    cagr, flag = compute_cagr(100, 50, 5)
    assert flag is None and cagr < 0

def test_cagr_exact_3yr_boundary():
    cagr, flag = compute_cagr(100, 100, 3)
    assert flag is None and round(cagr, 1) == 0.0