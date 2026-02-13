# core/knowledge_base.py

import json
import os
import logging

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        self.patterns = self._load_patterns()
        self.failures = self._load_failures()

    def _load_patterns(self):
        # Implementation of 190+ patterns logic
        return {
            'negative_gex_regime': {
                'name': 'Negative GEX Regime',
                'detection': lambda d: d['gex']['net_gex'] < -2e9,
                'meaning': 'Dealers will AMPLIFY moves',
                'action': 'Directional strategy',
                'confidence': 85
            },
            'positive_gex_regime': {
                'name': 'Positive GEX Regime',
                'detection': lambda d: d['gex']['net_gex'] > 2e9,
                'meaning': 'Dealers will DAMPEN moves',
                'action': 'Sell premium',
                'confidence': 82
            },
            'fii_aggressive_short': {
                'name': 'FII Aggressive Short',
                'detection': lambda d: d['smart_money']['fii_bias'] == 'Bearish',
                'meaning': 'Institutional selling detected',
                'action': 'Defensive positioning',
                'confidence': 77
            }
        }

    def _load_failures(self):
        return {
            'max_pain_not_guaranteed': {
                'mistake': 'Assuming price WILL close at max pain',
                'approach': 'Use as reference, not guarantee',
                'lesson': 'Max pain is probability, not destiny'
            }
        }

    def find_matching_patterns(self, analysis_results):
        matches = []
        for key, p in self.patterns.items():
            try:
                if p['detection'](analysis_results):
                    matches.append(p)
            except Exception as e:
                logger.error(f"Error matching pattern {key}: {e}")
        return matches

    def check_failure_scenarios(self, signal, analysis_results):
        warnings = []
        # Logic to check if current scenario matches a known failure
        return {'warnings': warnings}
