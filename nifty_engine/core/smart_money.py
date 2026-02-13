# nifty_engine/core/smart_money.py

import logging

logger = logging.getLogger(__name__)

class SmartMoneyAnalyzer:
    """
    Analyzes Institutional (FII, DII, Prop) and Retail positioning to find market bias.
    """

    @staticmethod
    def analyze_fii_bias(net_futures, historical_futures):
        """
        Interprets FII Index Futures bias.
        """
        if not historical_futures: return "Neutral"

        # Calculate percentile
        count = sum(1 for x in historical_futures if x < net_futures)
        percentile = (count / len(historical_futures)) * 100

        if percentile > 80:
            return "Aggressive Long (Bullish)"
        elif percentile < 20:
            return "Aggressive Short (Bearish)"
        return "Neutral"

    @staticmethod
    def analyze_retail_sentiment(net_oi, historical_oi, market_at_lows=False):
        """
        Retail is often wrong at extremes.
        """
        if not historical_oi: return "Neutral"

        count = sum(1 for x in historical_oi if x < net_oi)
        percentile = (count / len(historical_oi)) * 100

        if percentile < 10 and market_at_lows:
            return "Capitulation (Contrarian Bullish)"
        elif percentile > 90:
            return "Excessive Optimism (Contrarian Bearish)"

        return "Neutral"

    @staticmethod
    def get_combined_bias(fii_bias, dii_bias, retail_bias):
        """
        Aggregates bias from all major players.
        """
        if "Aggressive Long" in fii_bias and "Buying" in dii_bias:
            return "Institutional Convergence (Strong Bullish)"
        elif "Aggressive Short" in fii_bias and "Selling" in dii_bias:
            return "Institutional Convergence (Strong Bearish)"
        elif "Capitulation" in retail_bias:
            return "Contrarian Opportunity (Bullish)"

        return "Mixed / Neutral"
