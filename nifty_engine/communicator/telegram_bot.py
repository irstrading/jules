# nifty_engine/communicator/telegram_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from nifty_engine.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from nifty_engine.data.database import Database
from nifty_engine.core.market_engine import SmartMoney
import logging
import asyncio

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id
        self.application = None
        self.db = Database()

    async def start_bot(self):
        if not self.token or self.token == "YOUR_BOT_TOKEN":
            logger.warning("Telegram Bot Token not configured.")
            return

        self.application = ApplicationBuilder().token(self.token).build()

        # Command Handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("pcr", self.pcr_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stop", self.stop_command))

        logger.info("Telegram Bot Starting...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🚀 Nifty Engine Bot is Active!\nCommands:\n/pcr - Get current PCR\n/status - System status\n/stop - Emergency Stop")

    async def pcr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Fetch data from DB
        chart_df = self.db.get_last_candles("NIFTY", limit=1)
        if not chart_df.empty:
            # Example: In production, you'd store PCR in DB or calculate from live chain
            pcr = SmartMoney.calculate_pcr(1000000, 1200000)
            await update.message.reply_text(f"📊 Current Nifty PCR: {pcr} (Bullish)")
        else:
            await update.message.reply_text("⚠️ Data unavailable. Engine might be offline.")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        kill_switch = self.db.get_config("kill_switch", "OFF")
        status_text = f"🔄 System Status: {'🛑 STOPPED' if kill_switch == 'ON' else '▶️ RUNNING'}"
        await update.message.reply_text(status_text)

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.db.set_config("kill_switch", "ON")
        await update.message.reply_text("🛑 EMERGENCY STOP TRIGGERED! All trading halted.")

    async def send_alert(self, message):
        if not self.application or not self.chat_id:
            return
        try:
            await self.application.bot.send_message(chat_id=self.chat_id, text=f"🔔 *SIGNAL ALERT*:\n{message}", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")

    async def stop_bot(self):
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
