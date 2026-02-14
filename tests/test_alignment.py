from core.analyzers import IndexAlignment

def test_alignment():
    weights = {"RELIANCE": 10, "HDFCBANK": 10, "INFY": 5, "TCS": 5}
    # Case 1: All green
    dirs = {"RELIANCE": 1, "HDFCBANK": 1, "INFY": 1, "TCS": 1}
    res = IndexAlignment.calculate(dirs, weights)
    print(f"All Green: {res}")
    assert res['bullish_pct'] == 100.0
    assert "Strong Bullish" in res['status']

    # Case 2: 70% aligned
    # Total weight = 30. 70% of 30 = 21.
    # RELIANCE(10) + HDFCBANK(10) + INFY(5) = 25 (83.3%)
    dirs = {"RELIANCE": 1, "HDFCBANK": 1, "INFY": 1, "TCS": -1}
    res = IndexAlignment.calculate(dirs, weights)
    print(f"Mostly Green: {res}")
    assert res['bullish_pct'] > 70.0
    assert "Strong Bullish" in res['status']

    # Case 3: Mixed
    dirs = {"RELIANCE": 1, "HDFCBANK": -1, "INFY": 1, "TCS": -1}
    res = IndexAlignment.calculate(dirs, weights)
    print(f"Mixed: {res}")
    assert res['status'] == "Neutral"

if __name__ == "__main__":
    test_alignment()
    print("Alignment Test Passed!")
