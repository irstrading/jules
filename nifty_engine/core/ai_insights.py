# nifty_engine/core/ai_insights.py

import json

class AIInsights:
    def __init__(self, knowledge_base_path="nifty_engine/data/knowledge_base.json"):
        with open(knowledge_base_path, 'r') as f:
            self.kb = json.load(f)

    def generate_narrative(self, market_state):
        """
        Generates an AI-style natural language interpretation of the market.
        market_state: dict containing 'alignment', 'mmi', 'stock_states'
        """
        alignment = market_state.get('alignment', {})
        mmi = market_state.get('mmi', 50)
        stock_states = market_state.get('stock_states', {})

        narrative = []

        # 1. Trend Analysis
        if alignment.get('bullish_pct', 0) > 70:
            narrative.append("🚀 **Broad-based Bullishness:** The majority of the Nifty weight is aligned upward. This is a high-confidence rally.")
        elif alignment.get('bearish_pct', 0) > 70:
            narrative.append("📉 **Systemic Weakness:** Heavy selling across sectors. Avoid 'catching the falling knife'.")
        else:
            narrative.append("⚖️ **Sectoral Tug-of-War:** Market is split. Look for individual sector rotation.")

        # 2. Emotional State (MMI)
        if mmi < 30:
            narrative.append("🧤 **Smart Money Zone:** MMI shows Extreme Fear. Historically, this is where big players accumulate.")
        elif mmi > 70:
            narrative.append("⚠️ **Euphoria Alert:** MMI is in Extreme Greed. Retail is over-leveraged; a sharp 'shakeout' could be near.")

        # 3. Heavyweight Specifics
        reliance = stock_states.get('RELIANCE', {})
        hdfc = stock_states.get('HDFCBANK', {})

        if reliance.get('lp', 0) > reliance.get('pc', 0) and hdfc.get('lp', 0) > hdfc.get('pc', 0):
            narrative.append("💎 **The Twin Pillars:** Both Reliance and HDFC Bank are green. This provides a strong floor for Nifty.")
        elif reliance.get('lp', 0) < reliance.get('pc', 0) and hdfc.get('lp', 0) < hdfc.get('pc', 0):
            narrative.append("🧨 **Anchor Failure:** Reliance and HDFC Bank are both dragging the index down. High risk for Nifty.")

        # 4. Sector Rotation Logic (from KB)
        narrative.append(f"💡 **Rules Engine Advice:** {self.kb['market_rules']['SectorRotation']}")

        return narrative
