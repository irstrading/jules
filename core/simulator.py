# core/simulator.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class RealisticSimulator:
    """
    Advanced Institutional Simulation Engine.
    Generates correlated multi-index flows and realistic GBM price paths.
    """
    @staticmethod
    def generate_price_path(start_price, steps=100, drift=0.00005, volatility=0.005):
        """
        Refined GBM with mean-reversion tendencies for realistic intraday behavior.
        """
        price_path = [start_price]
        curr = start_price
        for _ in range(steps - 1):
            # GBM + Mean reversion to start price if it drifts too far
            mr_factor = (start_price - curr) * 0.01
            ret = np.random.normal(drift + mr_factor, volatility)
            curr = curr * np.exp(ret)
            price_path.append(curr)
        return np.array(price_path)

    @staticmethod
    def generate_stock_data(symbol, start_price, steps=100):
        # Align with clock minutes
        now = datetime.now().replace(second=0, microsecond=0)
        timestamps = [now - timedelta(minutes=i) for i in range(steps)]
        timestamps.reverse()

        prices = RealisticSimulator.generate_price_path(start_price, steps)

        # Noise injection for OHLC consistency
        opens = prices * (1 + np.random.normal(0, 0.0005, steps))
        closes = prices
        highs = np.maximum(opens, closes) * (1 + abs(np.random.normal(0, 0.001, steps)))
        lows = np.minimum(opens, closes) * (1 - abs(np.random.normal(0, 0.001, steps)))

        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': opens,
            'high': highs,
            'low': lows,
            'close': closes,
            'volume': np.random.randint(5000, 25000, steps)
        })
        return df

    @staticmethod
    def generate_market_state():
        # Correlated metrics
        sentiment_score = np.random.uniform(0.3, 0.9) # 0.3 to 0.9 range for "alive" feel

        bull_pct = round(sentiment_score * 100, 1)
        bear_pct = round((1 - sentiment_score) * 40, 1) # Not symmetric for realistic skew

        mmi = round(30 + (sentiment_score * 50) + np.random.uniform(-5, 5), 2)
        net_gex = round((sentiment_score - 0.5) * 6e9, 0) # Bias GEX based on sentiment

        return {
            "alignment": {
                "bullish_pct": bull_pct,
                "bearish_pct": bear_pct,
                "status": "Strong Bullish" if bull_pct > 70 else ("Weak Bearish" if bull_pct < 40 else "Neutral")
            },
            "mmi": mmi,
            "net_gex": net_gex,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
