# nifty_engine/core/market_engine.py

import numpy as np
from scipy.stats import norm
import pandas as pd

# ==========================================
# PART 1: OPTION GREEKS ENGINE (Black-Scholes)
# ==========================================
class Greeks:
    """
    Calculates the 'DNA' of an option price.
    """
    @staticmethod
    def calculate(flag, S, K, t, r, sigma):
        """
        flag: 'c' for Call, 'p' for Put
        S: Spot Price (Underlying)
        K: Strike Price
        t: Time to expiration (in years)
        r: Risk-free interest rate (e.g., 0.10 for 10%)
        sigma: Implied Volatility (e.g., 0.20 for 20%)
        """

        # Safety check for zero time
        if t <= 0:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}

        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)

        if flag == 'c':
            delta = norm.cdf(d1)
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(t)) - r * K * np.exp(-r * t) * norm.cdf(d2))
        else:
            delta = -norm.cdf(-d1)
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(t)) + r * K * np.exp(-r * t) * norm.cdf(-d2))

        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(t))
        vega = S * norm.pdf(d1) * np.sqrt(t)

        # Vomma: Sensitivity of Vega to Volatility
        vomma = vega * d1 * d2 / sigma

        return {
            'delta': round(delta, 3),
            'gamma': round(gamma, 6),
            'theta': round(theta / 365, 3), # Daily Theta decay
            'vega': round(vega / 100, 3),
            'vomma': round(vomma / 100, 3)
        }

# ==========================================
# PART 2: SMART MONEY ANALYSIS (OI Logic)
# ==========================================
class SmartMoney:
    """
    Interprets Open Interest to find what Big Players are doing.
    """
    @staticmethod
    def analyze_sentiment(price_change, oi_change):
        """
        Returns the market regime based on Price vs OI.
        """
        if price_change > 0 and oi_change > 0:
            return "Long Buildup (Bullish)"
            # Bulls are aggressive, adding new buy positions.

        elif price_change > 0 and oi_change < 0:
            return "Short Covering (Explosive Bullish)"
            # Bears are trapped and exiting fast. Price shoots up.

        elif price_change < 0 and oi_change > 0:
            return "Short Buildup (Bearish)"
            # Bears are aggressive, adding new sell positions.

        elif price_change < 0 and oi_change < 0:
            return "Long Unwinding (Bearish)"
            # Bulls are giving up and exiting. Price drops.

        return "Neutral"

    @staticmethod
    def calculate_pcr(call_oi_total, put_oi_total):
        """
        Put-Call Ratio.
        > 1.0 : Bullish (More Puts sold -> Support)
        < 0.6 : Bearish (More Calls sold -> Resistance)
        """
        if call_oi_total == 0: return 0
        return round(put_oi_total / call_oi_total, 2)

# ==========================================
# PART 3: ADVANCED GEX (Gamma Exposure)
# ==========================================
class GEX:
    """
    Calculates Gamma Exposure to find 'Magnetic Levels'.
    """
    @staticmethod
    def calculate_strike_gex(call_oi, put_oi, call_gamma, put_gamma, spot_price):
        """
        Returns the Net Gamma Exposure (in Crores/Billions depending on scale).
        Formula: OI * Gamma * Spot * 100 (Lot Multiplier assumption)
        """
        # Call GEX is Positive (Dealers Long Calls)
        call_gex = call_oi * call_gamma * spot_price * 0.01

        # Put GEX is Negative (Dealers Long Puts)
        put_gex = put_oi * put_gamma * spot_price * 0.01 * -1

        return call_gex + put_gex

# ==========================================
# PART 4: STRADDLE & OPTIONS ANALYSIS
# ==========================================
class OptionsAnalyzer:
    """
    Logic for Straddles, Strangles, and Option Chain Analysis.
    """
    @staticmethod
    def calculate_straddle_price(ce_price, pe_price):
        """Returns combined premium of CE and PE at the same strike."""
        return round(ce_price + pe_price, 2)

    @staticmethod
    def calculate_pcr_trend(oi_history):
        """
        Calculates PCR change over time.
        oi_history: list of dicts {'timestamp': ..., 'pcr': ...}
        """
        if len(oi_history) < 2:
            return 0
        return round(oi_history[-1]['pcr'] - oi_history[0]['pcr'], 4)

# ==========================================
# PART 5: MARKET MOOD INDEX (MMI)
# ==========================================
class MarketMoodIndex:
    """
    Composite sentiment index (0-100).
    """
    @staticmethod
    def calculate(pcr, iv_percentile, ad_ratio, oi_sentiment):
        """
        pcr: Put-Call Ratio (Expected 0.5 to 1.5)
        iv_percentile: 0 to 100
        ad_ratio: Advance/Decline Ratio (Expected 0.1 to 10)
        oi_sentiment: 1 for Bullish, -1 for Bearish, 0 for Neutral
        """
        # Normalize PCR (0.7 to 1.3 -> 0 to 100)
        pcr_score = np.clip((pcr - 0.7) / (1.3 - 0.7) * 100, 0, 100)

        # Normalize AD Ratio (0.5 to 2.0 -> 0 to 100)
        ad_score = np.clip((ad_ratio - 0.5) / (2.0 - 0.5) * 100, 0, 100)

        # Weighted average
        mmi = (pcr_score * 0.3) + (iv_percentile * 0.2) + (ad_score * 0.3) + ((oi_sentiment + 1) * 50 * 0.2)

        return round(mmi, 2)

    @staticmethod
    def get_regime(mmi):
        if mmi < 30: return "Extreme Fear (Bearish)"
        if mmi < 50: return "Fear (Cautious)"
        if mmi < 70: return "Greed (Bullish)"
        return "Extreme Greed (Overbought)"

    @staticmethod
    def calculate_ad_ratio(advances, declines):
        if declines == 0: return advances
        return round(advances / declines, 2)

# ==========================================
# PART 6: INDEX SENTIMENT ALIGNMENT (70% Rule)
# ==========================================
class IndexAlignment:
    """
    Calculates if the market is trending based on weighted stock/sector participation.
    """
    @staticmethod
    def calculate(stock_directions, weights):
        """
        stock_directions: dict {symbol: 1 for green, -1 for red, 0 for flat}
        weights: dict {symbol: weight_percentage}
        """
        bullish_weight = 0
        bearish_weight = 0
        total_tracked_weight = 0

        for symbol, direction in stock_directions.items():
            weight = weights.get(symbol, 0)
            total_tracked_weight += weight
            if direction == 1:
                bullish_weight += weight
            elif direction == -1:
                bearish_weight += weight

        bull_pct = (bullish_weight / total_tracked_weight) * 100 if total_tracked_weight > 0 else 0
        bear_pct = (bearish_weight / total_tracked_weight) * 100 if total_tracked_weight > 0 else 0

        status = "Neutral"
        if bull_pct >= 70:
            status = "Strong Bullish Trend (70%+ Aligned)"
        elif bear_pct >= 70:
            status = "Strong Bearish Trend (70%+ Aligned)"

        return {
            "bullish_pct": round(bull_pct, 1),
            "bearish_pct": round(bear_pct, 1),
            "status": status
        }

# ==========================================
# PART 7: STOCK-SPECIFIC SWING ANALYZER
# ==========================================
class StockAnalyzer:
    """
    Specialized analyzer for Stock Options (1-5 day swings).
    """
    @staticmethod
    def analyze_iv_regime(price_change, iv_change):
        if price_change > 0 and iv_change > 0:
            return "Accumulation (Rising IV + Price ↑)"
        elif price_change > 0 and iv_change < 0:
            return "Short Covering (Falling IV + Price ↑)"
        elif price_change < 0 and iv_change > 0:
            return "Panic / Fresh Shorts (Rising IV + Price ↓)"
        elif abs(price_change) < 0.5 and iv_change < 0:
            return "Option Selling (Falling IV + Range)"
        return "Neutral"

    @staticmethod
    def calculate_swing_score(data):
        """
        data: {
            'structure': 'BULLISH'|'BEARISH'|'SIDEWAYS',
            'sector_trend': 'SUPPORTIVE'|'DIVERGENT',
            'gex': float,
            'iv_trend': 'RISING'|'FALLING',
            'vomma': 'HIGH'|'LOW',
            'atm_oi': 'UNWINDING'|'BUILDUP'
        }
        """
        score = 0

        if data.get("structure") == "BULLISH": score += 2
        if data.get("sector_trend") == "SUPPORTIVE": score += 2
        if data.get("gex", 0) < 0: score += 1
        if data.get("iv_trend") == "RISING": score += 2
        if data.get("vomma") == "HIGH": score += 1
        if data.get("atm_oi") == "UNWINDING": score += 2

        # Result mapping
        if score >= 8: return "STRONG SWING BUY", score
        if score >= 6: return "CONDITIONAL BUY", score
        return "AVOID", score

if __name__ == "__main__":
    # Test Greeks
    greeks = Greeks.calculate('c', 24500, 24600, 0.02, 0.10, 0.15)
    print(f"Nifty 24600 CE Greeks: {greeks}")

    # Test Smart Money
    sentiment = SmartMoney.analyze_sentiment(price_change=50, oi_change=-15000)
    print(f"Market Sentiment: {sentiment}")
