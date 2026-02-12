# nifty_engine/strategies/ema_cross.py

from nifty_engine.strategies.base import BaseStrategy
from nifty_engine.core.indicators import Indicators
import pandas as pd

class EMACrossoverStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="EMA Crossover", symbol="NIFTY")
        self.fast_period = 9
        self.slow_period = 21

    def on_candle(self, df):
        if len(df) < self.slow_period + 1:
            return None

        close_prices = df['close']
        ema_fast = Indicators.ema(close_prices, self.fast_period)
        ema_slow = Indicators.ema(close_prices, self.slow_period)

        # Check for crossover
        if ema_fast.iloc[-2] <= ema_slow.iloc[-2] and ema_fast.iloc[-1] > ema_slow.iloc[-1]:
            return self.send_signal("BUY", df['close'].iloc[-1], "EMA 9 crossed above EMA 21")

        elif ema_fast.iloc[-2] >= ema_slow.iloc[-2] and ema_fast.iloc[-1] < ema_slow.iloc[-1]:
            return self.send_signal("SELL", df['close'].iloc[-1], "EMA 9 crossed below EMA 21")

        return None
