# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Angel One API
    ANGEL_API_KEY = os.getenv("ANGEL_ONE_API_KEY")
    ANGEL_CLIENT_ID = os.getenv("ANGEL_ONE_CLIENT_CODE")
    ANGEL_PASSWORD = os.getenv("ANGEL_ONE_PASSWORD")
    ANGEL_TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET")

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # Database
    DB_NAME = os.getenv("DB_NAME", "anza_production.db")

    # Analysis settings
    UPDATE_INTERVAL_SECONDS = 60
    RISK_FREE_RATE = 0.065
    NIFTY_LOT_SIZE = 50
    BANKNIFTY_LOT_SIZE = 25

    # Safety Limits
    MAX_CAPITAL_PER_TRADE = 0.05
    MAX_DAILY_LOSS_PCT = 3.0

    @staticmethod
    def validate():
        missing = []
        if not Settings.ANGEL_API_KEY: missing.append("ANGEL_ONE_API_KEY")
        if not Settings.ANGEL_CLIENT_ID: missing.append("ANGEL_ONE_CLIENT_CODE")
        if not Settings.ANGEL_TOTP_SECRET: missing.append("ANGEL_ONE_TOTP_SECRET")
        return missing

settings = Settings()
