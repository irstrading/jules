# nifty_engine/core/ingestor.py

import time
import pyotp
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from nifty_engine.config import (
    ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_CODE,
    ANGEL_ONE_PASSWORD, ANGEL_ONE_TOTP_SECRET
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AngelOneIngestor:
    def __init__(self):
        self.smart_api = None
        self.sws = None
        self.jwt_token = None
        self.refresh_token = None
        self.feed_token = None
        self.on_tick_callback = None

    def login(self):
        try:
            self.smart_api = SmartConnect(api_key=ANGEL_ONE_API_KEY)
            totp = pyotp.TOTP(ANGEL_ONE_TOTP_SECRET).now()
            data = self.smart_api.generateSession(ANGEL_ONE_CLIENT_CODE, ANGEL_ONE_PASSWORD, totp)

            if data['status']:
                self.jwt_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                self.feed_token = self.smart_api.getfeedToken()
                logger.info("Login Successful")
                return True
            else:
                logger.error(f"Login Failed: {data['message']}")
                # If error is about session already existing, we might need a different approach
                # but usually generateSession works fine.
                return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def refresh_session(self):
        """Attempts to refresh the JWT token using the refresh token."""
        try:
            if not self.refresh_token:
                return self.login()

            data = self.smart_api.renewAccessToken(self.refresh_token)
            if data['status']:
                self.jwt_token = data['data']['jwtToken']
                self.refresh_token = data['data']['refreshToken']
                logger.info("Session Refreshed Successfully")
                return True
            else:
                logger.warning(f"Session Refresh Failed: {data['message']}. Attempting full login...")
                return self.login()
        except Exception as e:
            logger.error(f"Error during session refresh: {e}")
            return self.login()

    def connect_websocket(self, correlation_id, action, mode, token_list):
        """
        Connects to the SmartWebSocketV2
        token_list format: [{"exchangeType": 1, "tokens": ["10626", "3045"]}]
        """
        try:
            self.sws = SmartWebSocketV2(self.jwt_token, ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_CODE, self.feed_token)

            def on_data(wsapp, msg):
                # logger.info(f"Ticks: {msg}")
                if self.on_tick_callback:
                    self.on_tick_callback(msg)

            def on_open(wsapp):
                logger.info("WebSocket Connected")
                self.sws.subscribe(correlation_id, mode, token_list)

            def on_error(wsapp, error):
                logger.error(f"WebSocket Error: {error}")

            def on_close(wsapp):
                logger.info("WebSocket Closed")

            self.sws.on_open = on_open
            self.sws.on_data = on_data
            self.sws.on_error = on_error
            self.sws.on_close = on_close

            self.sws.connect()
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}")

    def fetch_historical_data(self, symbol_token, exchange, interval, from_date, to_date):
        """
        Fetches historical candle data
        interval: ONE_MINUTE, FIVE_MINUTE, etc.
        """
        try:
            params = {
                "exchange": exchange,
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": from_date,
                "todate": to_date
            }
            data = self.smart_api.getCandleData(params)
            if data['status']:
                return data['data']
            else:
                logger.error(f"Failed to fetch historical data: {data['message']}")
                return None
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None

    def set_on_tick_callback(self, callback):
        self.on_tick_callback = callback

    def get_atm_strike(self, spot_price, base=50):
        """Calculates ATM strike based on spot price."""
        return round(spot_price / base) * base

    def get_option_symbols(self, underlying, expiry_date, strike_price):
        """
        In production, this would use a master contract file or API
        to find the specific CE/PE tokens for a given strike.
        For now, we'll implement a placeholder that simulates token discovery.
        """
        # Mocking token discovery for the sake of logic flow
        # In real life, you'd search the Angel One Scrip Master
        ce_token = f"OPT_{underlying}_{strike_price}_CE"
        pe_token = f"OPT_{underlying}_{strike_price}_PE"
        return ce_token, pe_token
