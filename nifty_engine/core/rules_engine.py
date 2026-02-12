# nifty_engine/core/rules_engine.py

import json
import os
from datetime import datetime
import pytz

class RulesEngine:
    def __init__(self, rules_path="nifty_engine/data/knowledge_base.json"):
        self.rules_path = rules_path
        self.rules = {}
        self.load_rules()

    def load_rules(self):
        if os.path.exists(self.rules_path):
            with open(self.rules_path, 'r') as f:
                data = json.load(f)
                # Extract rules part
                self.rules = data.get("market_rules", {})
                self.impact_behavior = data.get("impact_behavior", [])
                self.last_loaded = datetime.now()
        else:
            self.rules = {}
            self.impact_behavior = []
            self.last_loaded = None

    def refresh_knowledge(self):
        """
        Rapidly refreshes knowledge from the local file and potentially
        small external snippets without bloating storage.
        """
        self.load_rules()
        logger.info("Knowledge Base Refreshed.")
        return True

    def get_dynamic_context(self):
        """
        Returns real-time rules based on current time/date.
        """
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        current_time_str = now.strftime('%H:%M')

        dynamic_rules = {
            "current_time": current_time_str,
            "is_expiry_day": self._is_expiry_day(now),
            "special_alerts": []
        }

        # Rule: Expiry Day Gamma Acceleration
        if dynamic_rules["is_expiry_day"] and now.hour >= 13 and now.minute >= 30:
            dynamic_rules["special_alerts"].append(self.rules.get("ExpiryDay", "Expect high Gamma volatility"))

        return dynamic_rules

    def _is_expiry_day(self, dt):
        """
        Simplified: Check if today is Thursday (Nifty Expiry).
        In production, this should fetch an actual holiday/expiry calendar.
        """
        return dt.weekday() == 3 # Thursday

    def query_rule(self, category, key=None):
        if key:
            return self.rules.get(category, {}).get(key)
        return self.rules.get(category)
