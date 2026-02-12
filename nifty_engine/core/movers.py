# nifty_engine/core/movers.py

import json
import os

class NiftyMovers:
    def __init__(self, kb_path="nifty_engine/data/knowledge_base.json"):
        self.kb_path = kb_path
        self.weights = {}
        self.sectors = {}
        self.load_knowledge_base()

    def load_knowledge_base(self):
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r') as f:
                data = json.load(f)
                self.weights = data.get("nifty_50_weights", {})
                self.sectors = data.get("sectors", {})

    def calculate_contribution(self, stock_symbol, price_change_pct):
        """
        Calculates the contribution of a stock to the Nifty index move in points.
        Simplified formula: (Stock % Change * Weight) * NiftyBase / 100
        Assuming Nifty is at ~24000 for calculation scaling if needed,
        but usually it's just (PriceChangePct * Weight) / 100 * ScalingFactor.
        Professional way: (Weight in Index * Stock % Change)
        """
        weight = self.weights.get(stock_symbol, 0)
        # Nifty Move Contribution = (Stock % Change) * (Weight / 100) * (Current Nifty / Sum of Weights)
        # For simplicity, we'll return a relative 'Impact Score'
        return round(price_change_pct * weight, 2)

    def get_sector_performance(self, stock_data):
        """
        stock_data: dict {symbol: price_change_pct}
        """
        sector_perf = {}
        for sector, info in self.sectors.items():
            stocks = info.get("stocks", [])
            changes = [stock_data.get(s, 0) for s in stocks if s in stock_data]
            if changes:
                avg_change = sum(changes) / len(changes)
                sector_perf[sector] = round(avg_change, 2)
        return sector_perf

    def get_top_movers(self, stock_data):
        """
        Returns contributions of top heavyweights.
        """
        contributions = []
        for symbol, change in stock_data.items():
            if symbol in self.weights:
                impact = self.calculate_contribution(symbol, change)
                contributions.append({
                    "symbol": symbol,
                    "change": change,
                    "impact": impact
                })
        # Sort by impact absolute value
        return sorted(contributions, key=lambda x: abs(x['impact']), reverse=True)
