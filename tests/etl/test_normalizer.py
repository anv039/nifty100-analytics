import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src", "etl"))
from normalizer import normalize_year, normalize_ticker

def test_year_mar23(): assert normalize_year("Mar-23") == "2023-03"
def test_year_mar_space(): assert normalize_year("Mar 23") == "2023-03"
def test_year_march_full(): assert normalize_year("March-2023") == "2023-03"
def test_year_dec2012(): assert normalize_year("Dec 2012") == "2012-12"
def test_year_plain_int(): assert normalize_year("2023") == "2023-03"
def test_year_fy23(): assert normalize_year("FY23") == "2023-03"
def test_year_fy2023(): assert normalize_year("FY2023") == "2023-03"
def test_year_already_norm(): assert normalize_year("2023-03") == "2023-03"
def test_year_ttm(): assert normalize_year("TTM") is None
def test_year_garbage(): assert normalize_year("xyz") is None
def test_year_none(): assert normalize_year(None) is None
def test_year_jun(): assert normalize_year("Jun-23") == "2023-06"
def test_year_sep2024(): assert normalize_year("Sep 2024") == "2024-09"
def test_year_mar13(): assert normalize_year("Mar-13") == "2013-03"
def test_year_dec13(): assert normalize_year("Dec 2013") == "2013-12"

def test_ticker_strip(): assert normalize_ticker(" TCS ") == "TCS"
def test_ticker_lower(): assert normalize_ticker("tcs") == "TCS"
def test_ticker_hyphen(): assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"
def test_ticker_ampersand(): assert normalize_ticker("M&M") == "M&M"
def test_ticker_too_short(): assert normalize_ticker("A") is None
def test_ticker_none(): assert normalize_ticker(None) is None