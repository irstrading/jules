# tests/test_core.py

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from core.analyzers import Indicators, GreeksAnalyzer, SmartMoneyAnalyzer
from database.manager import DatabaseManager

def test_indicators():
    print("Testing Indicators...")
    data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 105, 104, 103, 102, 101] * 3,
        'high': [102] * 30,
        'low': [98] * 30,
        'volume': [1000] * 30
    })

    ema = Indicators.ema(data['close'], period=5)
    assert len(ema) == 30
    print("EMA OK")

    vwap = Indicators.vwap(data)
    assert len(vwap) == 30
    print("VWAP OK")

    rsi = Indicators.rsi(data['close'], period=14)
    assert len(rsi) == 30
    print("RSI OK")

def test_greeks():
    print("Testing Greeks...")
    analyzer = GreeksAnalyzer()
    res = analyzer.analyze({}) # Mock empty data
    assert 'call_greeks' in res
    assert 'put_greeks' in res
    print("Greeks OK")

if __name__ == "__main__":
    try:
        test_indicators()
        test_greeks()
        print("\nALL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
