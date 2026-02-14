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
        vega = S * norm.pdf(d1) * np.sqrt(t) # Note: Result is usually divided by 100 for percentage view

        return {
            'delta': round(delta, 3),
            'gamma': round(gamma, 6),
            'theta': round(theta / 365, 3), # Daily Theta decay
            'vega': round(vega / 100, 3)
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
# PART 4: HOW TO USE (Example)
# ==========================================
if __name__ == "__main__":
    # 1. Test Greeks
    greeks = Greeks.calculate('c', 24500, 24600, 0.02, 0.10, 0.15)
    print(f"Nifty 24600 CE Greeks: {greeks}")

    # 2. Test Smart Money
    sentiment = SmartMoney.analyze_sentiment(price_change=50, oi_change=-15000)
    print(f"Market Sentiment: {sentiment}")
