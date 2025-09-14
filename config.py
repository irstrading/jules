# -----------------------------------------------------------------------------
# Configuration File
# -----------------------------------------------------------------------------
# Please fill in your details below.

# --- Dhan API Credentials ---
# You need to generate these from your Dhan account.
# IMPORTANT: Keep these secret and do not share them publicly.
DHAN_CLIENT_ID = "YOUR_CLIENT_ID"
DHAN_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"


# --- Telegram Bot Credentials ---
# You need to create a bot with @BotFather on Telegram to get these.
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID" # This is your personal chat ID or a channel ID.


# --- Stock Universe ---
# List of stocks to scan. For now, a small sample.
# We will expand this to the full NIFTY 200 later.
STOCKS_TO_SCAN = [
    "RELIANCE",
    "HDFCBANK",
    "INFY",
    "ICICIBANK",
    "TCS"
]


# --- Scanner Settings ---
TIME_FRAMES = ["1H", "4H"]
# Note: For Dhan, 1H is available. 4H will be constructed by resampling 1H data.
