# nifty_engine/core/indicators.py

import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def sma(data, period=20):
        """Simple Moving Average"""
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data, period=20):
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def vwap(df):
        """Volume Weighted Average Price"""
        q = df['volume']
        p = (df['high'] + df['low'] + df['close']) / 3
        return (p * q).cumsum() / q.cumsum()

    @staticmethod
    def rsi(data, period=14):
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def stochastic_rsi(data, period=14, smooth_k=3, smooth_d=3):
        """Stochastic RSI"""
        rsi_val = Indicators.rsi(data, period)
        stoch_rsi = (rsi_val - rsi_val.rolling(period).min()) / (rsi_val.rolling(period).max() - rsi_val.rolling(period).min())
        k = stoch_rsi.rolling(smooth_k).mean() * 100
        d = k.rolling(smooth_d).mean()
        return k, d

    @staticmethod
    def macd(data, fast=12, slow=26, signal=9):
        """Moving Average Convergence Divergence"""
        exp1 = Indicators.ema(data, fast)
        exp2 = Indicators.ema(data, slow)
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def adx(df, period=14):
        """Average Directional Index"""
        df = df.copy()
        df['up_move'] = df['high'].diff()
        df['down_move'] = df['low'].diff().abs()

        df['+dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
        df['-dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

        df['tr'] = np.maximum(df['high'] - df['low'],
                             np.maximum((df['high'] - df['close'].shift(1)).abs(),
                                        (df['low'] - df['close'].shift(1)).abs()))

        atr = df['tr'].rolling(window=period).mean()
        plus_di = 100 * (df['+dm'].rolling(window=period).mean() / atr)
        minus_di = 100 * (df['-dm'].rolling(window=period).mean() / atr)

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        return adx
