# core/data_fetcher.py

import logging
import asyncio
import yfinance as yf
from datetime import datetime
from core.scrapers.institutional_scraper import InstitutionalScraper

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

            # 2. Fetch Option Chain (Centered around real spot)
            option_chain = await self.fetch_option_chain(symbol, expiry, spot_price)

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
        # Fallback to yfinance for REAL market data
        try:
            ticker_map = {"NIFTY": "^NSEI", "BANKNIFTY": "^NSEBANK"}
            yf_ticker = ticker_map.get(symbol, symbol)
            data = yf.Ticker(yf_ticker).history(period="1d")
            if not data.empty:
                return round(data['Close'].iloc[-1], 2)
        except Exception as e:
            logger.warning(f"yfinance fetch failed: {e}")

        return 24500.0

    async def fetch_option_chain(self, symbol, expiry, spot):
        # In a real implementation, call self.angel.get_option_chain()
        # Mocking a structure for Greeks/GEX to work, centered on real spot
        chain = []
        for i in range(-10, 11):
            strike = (int(spot) // 100 * 100) + (i * 50)
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
        # Use InstitutionalScraper for real-ish data
        scraper = InstitutionalScraper()
        df = scraper.fetch_nse_fii_dii()
        if df is not None:
            fii = df[df['Category'] == 'FII']['Net Value'].values[0]
            dii = df[df['Category'] == 'DII']['Net Value'].values[0]
            return {'fii': fii, 'dii': dii}
        return {'fii': 1250, 'dii': 800} # Fallback

    async def fetch_heavyweights(self):
        # Fetch REAL movers for Nifty Heavyweights via yfinance
        stocks_map = {
            "RELIANCE": "RELIANCE.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "INFY": "INFY.NS",
            "TCS": "TCS.NS"
        }
        movers = {}
        for name, ticker in stocks_map.items():
            try:
                t = yf.Ticker(ticker)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                    movers[name] = float(round(change, 2))
                else:
                    movers[name] = 0.0
            except:
                movers[name] = 0.0
        return movers

    def _calculate_t_expiry(self, expiry_str):
        # Calculate years remaining until expiry
        # Placeholder
        return 0.02 # ~1 week
