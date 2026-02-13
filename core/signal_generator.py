# core/signal_generator.py

import logging

logger = logging.getLogger(__name__)

class SignalGenerator:
    def generate_signals(self, analysis_results, matched_patterns):
        signals = []
        # Basic signal logic based on analysis
        if analysis_results['gex']['regime'] == 'Negative' and analysis_results['oi']['pcr'] < 0.7:
            signals.append({
                'strategy': 'Aggressive Call Buy',
                'direction': 'LONG',
                'confidence': 75,
                'entry': analysis_results['market_data']['spot_price'],
                'target': analysis_results['market_data']['spot_price'] + 200,
                'stop_loss': analysis_results['market_data']['spot_price'] - 100,
                'risk_reward': 2.0,
                'reasoning': 'Negative GEX expansion with Bullish PCR divergence',
                'symbol': 'NIFTY',
                'price': analysis_results['market_data']['spot_price']
            })
        return signals
