# services/angel_one.py

import pyotp
import logging
from SmartApi import SmartConnect
from config import settings

logger = logging.getLogger(__name__)

class AngelOneService:
    def __init__(self):
        self.smart_api = None
        self.jwt_token = None
        self.feed_token = None

    async def login(self):
        try:
            self.smart_api = SmartConnect(api_key=settings.ANGEL_API_KEY)
            totp = pyotp.TOTP(settings.ANGEL_TOTP_SECRET).now()
            data = self.smart_api.generateSession(settings.ANGEL_CLIENT_ID, settings.ANGEL_PASSWORD, totp)

            if data['status']:
                self.jwt_token = data['data']['jwtToken']
                self.feed_token = self.smart_api.getfeedToken()
                return True
            else:
                raise Exception(data['message'])
        except Exception as e:
            logger.error(f"Angel One Login Error: {e}")
            raise

    def get_spot_price(self, symbol="NIFTY"):
        # Placeholder for real LTP fetch
        # In production, this would call smart_api.ltpData
        return 24500.0

    def close(self):
        pass
