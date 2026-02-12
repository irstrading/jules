# nifty_engine/communicator/telegram_bot.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from nifty_engine.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import logging
import asyncio

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token=TELEGRAM_BOT_TOKEN, chat_id=TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id
        self.application = None

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
        await update.message.reply_text("🚀 Nifty Engine Bot is Active!\nCommands:\n/pcr - Get current PCR\n/status - Strategy status\n/stop - Emergency Stop")

    async def pcr_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # In a real app, this would fetch from the engine
        await update.message.reply_text("📊 Current Nifty PCR: 1.15 (Bullish)")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("🔄 System Status: RUNNING\nActive Strategies: EMA Crossover")

    async def stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Implementation to trigger emergency stop in the engine
        await update.message.reply_text("🛑 EMERGENCY STOP TRIGGERED!")

    async def send_alert(self, message):
        if not self.application or not self.chat_id:
            return
        await self.application.bot.send_message(chat_id=self.chat_id, text=f"🔔 *SIGNAL ALERT*:\n{message}", parse_mode='Markdown')

    async def stop_bot(self):
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
