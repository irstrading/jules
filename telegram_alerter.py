# -----------------------------------------------------------------------------
# Telegram Alerter
# -----------------------------------------------------------------------------
# This module handles sending alerts via a Telegram bot.
# -----------------------------------------------------------------------------

import telegram
import config

def send_telegram_alert(message):
    """
    Sends a message to a specified Telegram chat.

    Args:
        message (str): The message to send.
    """
    if not config.TELEGRAM_BOT_TOKEN or config.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Telegram Bot Token not configured. Skipping alert.")
        print(f"Alert Message:\n{message}")
        return

    try:
        bot = telegram.Bot(token=config.TELEGRAM_BOT_TOKEN)
        bot.send_message(
            chat_id=config.TELEGRAM_CHAT_ID,
            text=message,
            parse_mode=telegram.ParseMode.MARKDOWN
        )
        print("Telegram alert sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
