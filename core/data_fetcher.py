# core/data_fetcher.py

import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class DataFetcher:
    """
    Handles data retrieval from Angel One Broker API.
    Provides a unified market data object for the analyzers.
    """
    def __init__(self, angel_service):
        self.angel = angel_service
        self.last_data = None

    async def fetch_all_data(self, symbol="NIFTY", expiry=None):
        """
        Main entry point for data collection.
        In demo mode, this returns simulated data.
        In live mode, it calls Angel One.
        """
        try:
            # 1. Fetch Spot Price
            spot_price = await self.fetch_spot(symbol)

            # 2. Fetch Option Chain
            option_chain = await self.fetch_option_chain(symbol, expiry)

            # 3. Fetch Institutional Data
            fii_dii = await self.fetch_institutional_flow()

            # 4. Fetch Heavyweights
            heavyweights = await self.fetch_heavyweights()

            data = {
                'timestamp': datetime.now(),
                'symbol': symbol,
                'spot_price': spot_price,
                'option_chain': option_chain,
                'time_to_expiry': self._calculate_t_expiry(expiry),
                'fii_net_cash': fii_dii['fii'],
                'dii_net_cash': fii_dii['dii'],
                'heavyweights': heavyweights
            }

            self.last_data = data
            return data

        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return self.last_data # Return cached data on failure

    async def fetch_spot(self, symbol):
        # In a real implementation, call self.angel.get_ltp()
        # For now, return a placeholder or dummy
        return 24500.0

    async def fetch_option_chain(self, symbol, expiry):
        # In a real implementation, call self.angel.get_option_chain()
        # Mocking a structure for Greeks/GEX to work
        chain = []
        spot = 24500
        for i in range(-10, 11):
            strike = (spot // 100 * 100) + (i * 50)
            chain.append({
                'strike': strike,
                'call_ltp': 100 + (spot - strike) * 0.5,
                'put_ltp': 100 + (strike - spot) * 0.5,
                'call_oi': 50000 + abs(i) * 1000,
                'put_oi': 40000 + abs(i) * 1000,
                'call_iv': 0.15 + (abs(i) * 0.005),
                'put_iv': 0.16 + (abs(i) * 0.005),
            })
        return chain

    async def fetch_institutional_flow(self):
        # This would typically scrape NSE or use a premium API
        return {'fii': 1250, 'dii': 800} # Net values in Crores

    async def fetch_heavyweights(self):
        # Simulated movers for Nifty Heavyweights
        import numpy as np
        stocks = ["RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "LT", "TATAMOTORS", "AXISBANK"]
        return {s: round(np.random.uniform(-2.0, 3.0), 2) for s in stocks}

    def _calculate_t_expiry(self, expiry_str):
        # Calculate years remaining until expiry
        # Placeholder
        return 0.02 # ~1 week
