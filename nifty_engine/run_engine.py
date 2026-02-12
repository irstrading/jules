# nifty_engine/run_engine.py

import asyncio
import logging
from nifty_engine.core.ingestor import AngelOneIngestor
from nifty_engine.data.database import Database
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.communicator.telegram_bot import TelegramBot
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NiftyEngine:
    def __init__(self):
        self.db = Database()
        self.ingestor = AngelOneIngestor()
        self.strategy_manager = StrategyManager()
        self.bot = TelegramBot()
        self.running = False

    async def start(self):
        logger.info("Initializing Nifty Engine...")

        # 1. Load Strategies
        self.strategy_manager.load_strategies()

        # 2. Login to Angel One
        # if not self.ingestor.login():
        #    logger.error("Failed to login to Angel One. System will run in simulation mode.")

        # 3. Start Telegram Bot
        await self.bot.start_bot()

        # 4. Warm up (Historical Patching - Mocked for now)
        await self.warm_up()

        self.running = True
        logger.info("Nifty Engine is now running!")

        # 5. Connect WebSocket (Mocked for now)
        # self.ingestor.set_on_tick_callback(self.on_tick)
        # self.ingestor.connect_websocket(...)

    async def warm_up(self):
        logger.info("Warming up with last 5 days of data...")
        # In a real scenario, call ingestor.fetch_historical_data
        pass

    def on_tick(self, tick):
        # Process live ticks
        pass

    def on_candle_closed(self, symbol, candle_df):
        # Save to DB
        self.db.save_candles(candle_df, symbol)

        # Run strategies
        signals = self.strategy_manager.run_on_candle(symbol, candle_df)

        # Handle signals
        for signal in signals:
            self.db.log_alert(signal['symbol'], signal['message'], signal['strategy'])
            asyncio.create_task(self.bot.send_alert(f"[{signal['strategy']}] {signal['symbol']}: {signal['message']} at {signal['price']}"))

    async def stop(self):
        self.running = False
        await self.bot.stop_bot()
        logger.info("Nifty Engine stopped.")

async def main():
    engine = NiftyEngine()
    try:
        await engine.start()
        # Keep running until cancelled
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        await engine.stop()
    except KeyboardInterrupt:
        await engine.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
