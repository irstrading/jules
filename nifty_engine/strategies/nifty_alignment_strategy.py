# nifty_engine/strategies/nifty_alignment_strategy.py

from nifty_engine.strategies.base import BaseStrategy
from nifty_engine.core.indicators import Indicators
import pandas as pd

class NiftyAlignmentStrategy(BaseStrategy):
    name = "Nifty70Alignment"
    instruments = ["NIFTY"]
    timeframe = "1m"

    def __init__(self):
        super().__init__()
        self.last_signal = None

    def on_candle(self, df, context):
        """
        Uses the 70% Index Alignment rule + EMA trend.
        """
        if df is None or len(df) < 20:
            return None

        # 1. Check Alignment from Context
        alignment = context.get('alignment', {})
        bullish_pct = alignment.get('bullish_pct', 0)
        bearish_pct = alignment.get('bearish_pct', 0)

        # 2. Technical Trend (EMA 20)
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        current_price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        ema20 = df['ema20'].iloc[-1]

        # 3. Strategy Logic
        # BUY: Alignment > 70% Bullish AND Price > EMA 20
        if bullish_pct >= 70 and current_price > ema20:
            if self.last_signal != "BUY":
                self.last_signal = "BUY"
                return self.send_signal("BUY", current_price, f"Nifty Aligned Bullish ({bullish_pct}%) & above EMA20")

        # SELL: Alignment > 70% Bearish AND Price < EMA 20
        elif bearish_pct >= 70 and current_price < ema20:
            if self.last_signal != "SELL":
                self.last_signal = "SELL"
                return self.send_signal("SELL", current_price, f"Nifty Aligned Bearish ({bearish_pct}%) & below EMA20")

        # EXIT: Alignment falls below 50%
        elif self.last_signal == "BUY" and bullish_pct < 50:
            self.last_signal = None
            return self.send_signal("EXIT", current_price, "Bullish Alignment weakened")

        elif self.last_signal == "SELL" and bearish_pct < 50:
            self.last_signal = None
            return self.send_signal("EXIT", current_price, "Bearish Alignment weakened")

        return None
