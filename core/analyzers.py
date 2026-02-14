# core/analyzers.py

import numpy as np
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)

class GreeksAnalyzer:
    """
    Implements Black-Scholes model for institutional Greeks.
    """
    @staticmethod
    def calculate_bs(flag, S, K, t, r, sigma):
        """
        flag: 'c' or 'p'
        S: Spot Price
        K: Strike Price
        t: Time to expiry (years)
        r: Risk free rate
        sigma: Implied Volatility
        """
        if t <= 0:
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}

        try:
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

            return {
                'delta': round(delta, 4),
                'gamma': round(gamma, 6),
                'theta': round(theta / 365, 4),
                'vega': round(vega / 100, 4)
            }
        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0}

    def analyze(self, market_data):
        """
        Batch calculates greeks for the entire option chain.
        """
        results = {'call_greeks': {}, 'put_greeks': {}}
        spot = market_data.get('spot_price', 0)
        t = market_data.get('time_to_expiry', 0.01) # Default 1% of a year
        r = 0.10 # 10% risk free rate

        chain = market_data.get('option_chain', [])
        for strike_data in chain:
            strike = strike_data['strike']

            # Call
            iv_c = strike_data.get('call_iv', 0.15)
            results['call_greeks'][strike] = self.calculate_bs('c', spot, strike, t, r, iv_c)

            # Put
            iv_p = strike_data.get('put_iv', 0.15)
            results['put_greeks'][strike] = self.calculate_bs('p', spot, strike, t, r, iv_p)

        return results

class GEXAnalyzer:
    """
    Gamma Exposure (GEX) Analysis.
    Helps identify market maker hedging requirements.
    """
    def analyze(self, market_data, greeks_results):
        net_gex = 0
        chain = market_data.get('option_chain', [])
        spot = market_data.get('spot_price', 0)

        for strike_data in chain:
            strike = strike_data['strike']
            call_oi = strike_data.get('call_oi', 0)
            put_oi = strike_data.get('put_oi', 0)

            c_gamma = greeks_results['call_greeks'].get(strike, {}).get('gamma', 0)
            p_gamma = greeks_results['put_greeks'].get(strike, {}).get('gamma', 0)

            # Net Gamma Exposure Formula: (Call OI * Call Gamma - Put OI * Put Gamma) * Spot * Multiplier
            # We assume a lot size multiplier of 50 for Nifty
            strike_gex = (call_oi * c_gamma - put_oi * p_gamma) * spot * 50
            net_gex += strike_gex

        regime = "Positive (Stabilizing)" if net_gex > 0 else "Negative (Accelerating)"

        return {
            'net_gex': round(net_gex, 2),
            'regime': regime,
            'gex_flip_level': self._calculate_flip_level(market_data, greeks_results)
        }

    def _calculate_flip_level(self, market_data, greeks_results):
        # Simplistic flip level: strike with highest absolute gamma exposure
        return market_data.get('spot_price', 0) # Placeholder for more complex calculation

class OIAnalyzer:
    """
    Open Interest and Sentiment Analysis.
    """
    def analyze(self, market_data):
        total_call_oi = sum(s.get('call_oi', 0) for s in market_data.get('option_chain', []))
        total_put_oi = sum(s.get('put_oi', 0) for s in market_data.get('option_chain', []))

        pcr = total_put_oi / total_call_oi if total_call_oi > 0 else 0

        # Identify Max Pain
        max_pain = self._calculate_max_pain(market_data.get('option_chain', []))

        return {
            'pcr': round(pcr, 3),
            'total_call_oi': total_call_oi,
            'total_put_oi': total_put_oi,
            'max_pain': max_pain,
            'regime': "Bullish" if pcr > 1.1 else "Bearish" if pcr < 0.7 else "Neutral"
        }

    def _calculate_max_pain(self, chain):
        # Placeholder for real Max Pain calculation
        if not chain: return 0
        return chain[len(chain)//2]['strike']

class SmartMoneyAnalyzer:
    """
    Institutional Flow and Cycle Analysis.
    """
    def analyze(self, market_data):
        # In live mode, this would fetch from InstitutionalScraper
        fii_cash = market_data.get('fii_net_cash', 0)
        dii_cash = market_data.get('dii_net_cash', 0)

        bias = "Strong Bullish" if fii_cash > 0 and dii_cash > 0 else \
               "Strong Bearish" if fii_cash < 0 and dii_cash < 0 else \
               "Mixed"

        return {
            'fii_bias': "Bullish" if fii_cash > 0 else "Bearish",
            'dii_bias': "Bullish" if dii_cash > 0 else "Bearish",
            'net_bias': bias,
            'flow_magnitude': abs(fii_cash) + abs(dii_cash)
        }

    @staticmethod
    def identify_cycle_phase(cash_flow_ma, price_trend):
        if cash_flow_ma > 500 and price_trend == "SIDEWAYS":
            return "ACCUMULATION", "Smart money is buying while public is fearful."
        elif cash_flow_ma > 1000 and price_trend == "UP":
            return "MARKUP", "Institutional support is strong. Trend is sustainable."
        elif cash_flow_ma < -500 and price_trend == "SIDEWAYS":
            return "DISTRIBUTION", "Smart money is exiting while public is buying."
        elif cash_flow_ma < -1000 and price_trend == "DOWN":
            return "MARKDOWN", "Institutional exit confirmed. Avoid buying dip."
        return "NEUTRAL", "Market is in a decision phase."

class Indicators:
    @staticmethod
    def ema(series, period=20):
        if len(series) < period: return series
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def vwap(df):
        if 'volume' not in df.columns: return df['close']
        return (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()

    @staticmethod
    def rsi(series, period=14):
        if len(series) < period: return series
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class IndexAlignment:
    @staticmethod
    def calculate(directions, weights):
        total_weight = sum(weights.values())
        if total_weight == 0:
            return {'bullish_pct': 0, 'bearish_pct': 0, 'status': 'Neutral'}

        bull_w = sum(weights[t] for t, d in directions.items() if d > 0)
        bear_w = sum(weights[t] for t, d in directions.items() if d < 0)

        bull_pct = (bull_w / total_weight) * 100
        bear_pct = (bear_w / total_weight) * 100

        if bull_pct >= 70: status = "Strong Bullish (70% Aligned)"
        elif bear_pct >= 70: status = "Strong Bearish (70% Aligned)"
        else: status = "Neutral"

        return {'bullish_pct': round(bull_pct, 1), 'bearish_pct': round(bear_pct, 1), 'status': status}
