# core/simulator.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class RealisticSimulator:
    """
    Generates realistic market data for Demo Mode.
    """
    @staticmethod
    def generate_price_path(start_price, steps=100, drift=0.0001, volatility=0.01):
        """
        Geometric Brownian Motion for realistic price movement.
        """
        returns = np.random.normal(drift, volatility, steps)
        price_path = start_price * np.exp(np.cumsum(returns))
        return price_path

    @staticmethod
    def generate_stock_data(symbol, start_price, steps=100):
        timestamps = pd.date_range(end=datetime.now(), periods=steps, freq='1min')
        prices = RealisticSimulator.generate_price_path(start_price, steps)
        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': prices * (1 + np.random.normal(0, 0.001, steps)),
            'high': prices * (1 + abs(np.random.normal(0, 0.002, steps))),
            'low': prices * (1 - abs(np.random.normal(0, 0.002, steps))),
            'close': prices,
            'volume': np.random.randint(1000, 10000, steps)
        })
        return df

    @staticmethod
    def generate_market_state():
        alignment = {
            "bullish_pct": round(np.random.uniform(40, 90), 1),
            "bearish_pct": round(np.random.uniform(10, 40), 1),
            "status": "Strong Bullish Trend" if np.random.random() > 0.5 else "Neutral"
        }
        mmi = round(np.random.uniform(20, 80), 2)
        net_gex = round(np.random.uniform(-3e9, 3e9), 0)

        return {
            "alignment": alignment,
            "mmi": mmi,
            "net_gex": net_gex,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
