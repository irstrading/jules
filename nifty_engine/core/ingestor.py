# nifty_engine/core/ingestor.py

import time
import pyotp
import requests
import json
import os
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

    def download_scrip_master(self):
        """Downloads the latest scrip master from Angel One."""
        url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        try:
            logger.info("Downloading Scrip Master...")
            response = requests.get(url)
            if response.status_code == 200:
                with open("scrip_master.json", "w") as f:
                    f.write(response.text)
                logger.info("Scrip Master downloaded successfully.")
                return True
            else:
                logger.error(f"Failed to download Scrip Master: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error downloading Scrip Master: {e}")
            return False

    def get_option_symbols(self, underlying, expiry_date, strike_price):
        """
        Searches the Scrip Master for the specific CE/PE tokens.
        underlying: e.g., 'NIFTY'
        expiry_date: e.g., '27FEB2025' (Format depends on scrip master)
        """
        if not os.path.exists("scrip_master.json"):
            self.download_scrip_master()

        try:
            with open("scrip_master.json", "r") as f:
                scrip_data = json.load(f)

            ce_token = None
            pe_token = None

            for item in scrip_data:
                if item['exch_seg'] == 'NFO' and underlying in item['symbol'] and expiry_date in item['expiry']:
                    try:
                        # Convert strike to float for comparison
                        item_strike = float(item['strike']) / 100 # Sometimes strikes are multiplied by 100
                        if abs(item_strike - strike_price) < 1: # Tolerance for float comparison
                            if item['symbol'].endswith('CE'):
                                ce_token = item['token']
                            elif item['symbol'].endswith('PE'):
                                pe_token = item['token']
                    except:
                        continue

                if ce_token and pe_token:
                    break

            return ce_token, pe_token
        except Exception as e:
            logger.error(f"Error searching Scrip Master: {e}")
            return None, None
