from app.oi_engine import StrikeData, classify_pair, ratio

def s(k, cc, pc, co=100, po=120, cl=10, pl=12):
    return StrikeData(k, co, po, cc, pc, cl, pl)

def test_strong_bullish():
    assert classify_pair(s(90, 50, -25), s(100, 60, -35)) == "Strong Bullish"

def test_strong_bearish():
    assert classify_pair(s(90, -35, 60), s(100, -25, 50)) == "Strong Bearish"

def test_initially_bullish():
    assert classify_pair(s(90, 40, 60), s(100, 45, 50)) == "Initially Bullish"

def test_initially_bearish():
    assert classify_pair(s(90, 45, 50), s(100, 60, 40)) == "Initially Bearish"

def test_neutral():
    assert classify_pair(s(90, 50, 50), s(100, 40, 45)) == "Neutral / No Setup"

def test_ratio_zero_denominator():
    assert ratio(100, 0) is None
    assert ratio(120, 60) == 2
