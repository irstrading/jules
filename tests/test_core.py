# tests/test_core.py

import sys
import os
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from nifty_engine.core.indicators import Indicators
from nifty_engine.core.market_engine import Greeks, SmartMoney
from nifty_engine.core.rules_engine import RulesEngine
from nifty_engine.data.database import Database

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
    # flag, S, K, t, r, sigma
    res = Greeks.calculate('c', 24500, 24500, 0.02, 0.10, 0.15)
    assert 'delta' in res
    assert 'gamma' in res
    assert res['delta'] > 0
    print("Greeks OK")

def test_rules_engine():
    print("Testing Rules Engine...")
    re = RulesEngine()
    context = re.get_dynamic_context()
    assert 'current_time' in context
    assert 'is_expiry_day' in context
    print("Rules Engine OK")

if __name__ == "__main__":
    try:
        test_indicators()
        test_greeks()
        test_rules_engine()
        print("\nALL TESTS PASSED!")
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
