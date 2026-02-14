# core/strategy_engine.py

import numpy as np
import pandas as pd

class StrategyLab:
    """
    Core engine for strategy modeling and payoff calculations.
    """
    @staticmethod
    def calculate_payoff(spot_range, legs):
        """
        legs: list of dicts {
            'type': 'CE'|'PE',
            'action': 'BUY'|'SELL',
            'strike': float,
            'premium': float,
            'qty': int
        }
        """
        total_payoff = np.zeros_like(spot_range)
        net_credit_debit = 0

        for leg in legs:
            strike = leg['strike']
            premium = leg['premium']
            qty = leg['qty']
            multiplier = 1 if leg['action'] == 'BUY' else -1

            if leg['type'] == 'CE':
                payoff = np.maximum(0, spot_range - strike) - premium
            else:
                payoff = np.maximum(0, strike - spot_range) - premium

            total_payoff += payoff * qty * multiplier
            net_credit_debit += premium * qty * multiplier

        return total_payoff, net_credit_debit

    @staticmethod
    def get_strategy_metrics(spot_range, payoff):
        max_profit = np.max(payoff)
        max_loss = np.min(payoff)

        # Find breakevens (where payoff crosses zero)
        breakevens = []
        for i in range(len(payoff) - 1):
            if (payoff[i] <= 0 and payoff[i+1] > 0) or (payoff[i] >= 0 and payoff[i+1] < 0):
                # Linear interpolation for more accurate breakeven
                x1, x2 = spot_range[i], spot_range[i+1]
                y1, y2 = payoff[i], payoff[i+1]
                be = x1 - y1 * (x2 - x1) / (y2 - y1)
                breakevens.append(round(be, 2))

        return {
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "breakevens": breakevens
        }
