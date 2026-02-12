# nifty_engine/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Angel One API configuration
ANGEL_ONE_API_KEY = os.getenv("ANGEL_ONE_API_KEY")
ANGEL_ONE_CLIENT_CODE = os.getenv("ANGEL_ONE_CLIENT_CODE")
ANGEL_ONE_PASSWORD = os.getenv("ANGEL_ONE_PASSWORD")
ANGEL_ONE_TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Database Configuration
DB_NAME = os.getenv("DB_NAME", "nifty_data.db")

# Trading Settings
NIFTY_SYMBOL = os.getenv("NIFTY_SYMBOL", "NIFTY")
BANKNIFTY_SYMBOL = os.getenv("BANKNIFTY_SYMBOL", "BANKNIFTY")
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "1m")

# Security Check
def validate_config():
    missing = []
    if not ANGEL_ONE_API_KEY: missing.append("ANGEL_ONE_API_KEY")
    if not ANGEL_ONE_CLIENT_CODE: missing.append("ANGEL_ONE_CLIENT_CODE")
    if not ANGEL_ONE_TOTP_SECRET: missing.append("ANGEL_ONE_TOTP_SECRET")

    if missing:
        print(f"⚠️ WARNING: Missing configuration for: {', '.join(missing)}")
        print("Please check your .env file.")
        return False
    return True
