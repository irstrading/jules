# nifty_engine/strategies/smart_nifty.py

from nifty_engine.strategies.base import BaseStrategy
from nifty_engine.core.indicators import Indicators
import pandas as pd

class SmartNiftyStrategy(BaseStrategy):
    name = "Smart Nifty Intelligence"
    instruments = ["NIFTY"]
    timeframe = "1m"

    def __init__(self):
        super().__init__()
        self.vwap_period = 20

    def on_candle(self, df, context):
        """
        Advanced strategy that combines Technicals with Contextual Intelligence
        """
        if len(df) < self.vwap_period:
            return None

        current_price = df['close'].iloc[-1]
        vwap = Indicators.vwap(df).iloc[-1]
        rsi = Indicators.rsi(df['close']).iloc[-1]

        # Get Context Data
        movers = context.get('movers', {})
        rules = context.get('rules', {})

        # Check Heavyweight Strength (Reliance and HDFCBANK)
        heavyweight_strength = movers.get('Reliance Strength', 0) + movers.get('HDFCBANK Strength', 0)

        # LOGIC:
        # 1. Price above VWAP (Bullish Trend)
        # 2. RSI not overbought (< 70)
        # 3. Heavyweights are showing positive strength

        if current_price > vwap and rsi < 70 and heavyweight_strength > 0.5:
            msg = f"Bullish: Price > VWAP and Heavyweights Strong ({heavyweight_strength:.2f})"
            return self.send_signal("BUY", current_price, msg)

        elif current_price < vwap and rsi > 30 and heavyweight_strength < -0.5:
            msg = f"Bearish: Price < VWAP and Heavyweights Weak ({heavyweight_strength:.2f})"
            return self.send_signal("SELL", current_price, msg)

        return None
