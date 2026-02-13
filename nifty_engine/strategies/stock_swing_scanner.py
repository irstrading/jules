# nifty_engine/strategies/stock_swing_scanner.py

from nifty_engine.strategies.base import BaseStrategy
from nifty_engine.core.market_engine import StockAnalyzer
import pandas as pd

class StockSwingScanner(BaseStrategy):
    name = "StockSwingScanner"
    instruments = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "AXISBANK", "LT", "TATAMOTORS"]
    timeframe = "1m"

    def __init__(self):
        super().__init__()
        self.last_scores = {} # {symbol: score}

    def on_candle(self, df, context):
        """
        Calculates 1-5 day swing score based on 6 core signals.
        """
        symbol = context.get('symbol', self.symbol)
        if df is None or len(df) < 5:
            return None

        # 1. Structure (Simplified: Higher Close than 5 candles ago)
        structure = "BULLISH" if df['close'].iloc[-1] > df['close'].iloc[-5] else "BEARISH"

        # 2. Sector Trend (From Context)
        sector_trend = "SUPPORTIVE" # Default for demo

        # 3. GEX (Placeholder logic)
        gex_val = -100 # Assume Negative for expansion signal

        # 4. IV Trend (Simplified)
        iv_trend = "RISING"

        # 5. Vomma
        vomma_status = "HIGH"

        # 6. ATM OI
        atm_oi_status = "UNWINDING"

        data = {
            'structure': structure,
            'sector_trend': sector_trend,
            'gex': gex_val,
            'iv_trend': iv_trend,
            'vomma': vomma_status,
            'atm_oi': atm_oi_status
        }

        signal_text, score = StockAnalyzer.calculate_swing_score(data)

        if score >= 6 and self.last_scores.get(symbol, 0) < 6:
            self.last_scores[symbol] = score
            return self.send_signal(signal_text, df['close'].iloc[-1], f"Swing Score: {score}/10 | {symbol}")

        self.last_scores[symbol] = score
        return None
