# nifty_engine/run_engine.py

import asyncio
import logging
from nifty_engine.core.ingestor import AngelOneIngestor
from nifty_engine.data.database import Database
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.communicator.telegram_bot import TelegramBot
from nifty_engine.config import NIFTY_SYMBOL
import pandas as pd
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NiftyEngine:
    def __init__(self):
        self.db = Database()
        self.ingestor = AngelOneIngestor()
        self.strategy_manager = StrategyManager(self.db)
        self.bot = TelegramBot()
        self.running = False
        self.tick_data = [] # Buffer for ticks to aggregate into candles

    async def start(self):
        logger.info("Initializing Nifty Engine...")

        # 0. Load Strategies
        self.strategy_manager.load_strategies()

        # 1. Reset Kill Switch on startup (optional, user might want to keep it)
        self.db.set_config("kill_switch", "OFF")

        # 2. Start Telegram Bot
        await self.bot.start_bot()

        # 3. Login to Angel One
        # In production, this would be:
        # if self.ingestor.login():
        #     self.ingestor.set_on_tick_callback(self.on_tick)
        #     # Subscribe to NIFTY (Token for NIFTY Index is usually '99926000' for NSE)
        #     self.ingestor.connect_websocket("nifty_feed", 1, 1, [{"exchangeType": 1, "tokens": ["99926000"]}])

        self.running = True
        logger.info("Nifty Engine is now running!")

    def on_tick(self, tick):
        """Callback for live ticks"""
        if self.db.get_config("kill_switch") == "ON":
            return

        # Example tick processing
        # tick usually contains 'lp' (last price), 'v' (volume), etc.
        self.tick_data.append({
            'timestamp': datetime.now(),
            'price': float(tick.get('lp', 0)),
            'volume': int(tick.get('v', 0))
        })

    async def aggregate_candles_loop(self):
        """Background loop to aggregate ticks into 1-minute candles"""
        while self.running:
            await asyncio.sleep(60) # Wait for 1 minute

            if not self.tick_data:
                continue

            df_ticks = pd.DataFrame(self.tick_data)
            self.tick_data = [] # Clear buffer

            # Create 1-minute candle
            candle = {
                'timestamp': df_ticks['timestamp'].iloc[0].replace(second=0, microsecond=0),
                'open': df_ticks['price'].iloc[0],
                'high': df_ticks['price'].max(),
                'low': df_ticks['price'].min(),
                'close': df_ticks['price'].iloc[-1],
                'volume': df_ticks['volume'].sum()
            }

            df_candle = pd.DataFrame([candle])
            self.on_candle_closed(NIFTY_SYMBOL, df_candle)

    def on_candle_closed(self, symbol, candle_df):
        # Save to DB
        self.db.save_candles(candle_df, symbol)

        # Sync strategy status from DB before running
        self.strategy_manager.sync_with_db()

        # Fetch last candles for technical analysis
        history_df = self.db.get_last_candles(symbol, limit=100)

        # Run strategies
        signals = self.strategy_manager.run_on_candle(symbol, history_df)

        # Handle signals
        for signal in signals:
            self.db.log_alert(signal['symbol'], signal['message'], signal['strategy'])
            asyncio.create_task(self.bot.send_alert(f"[{signal['strategy']}] {signal['symbol']}: {signal['message']} at {signal['price']}"))

    async def monitor_system_loop(self):
        """Monitor for Kill Switch or Strategy updates from UI"""
        while self.running:
            self.strategy_manager.sync_with_db()
            if self.db.get_config("kill_switch") == "ON" and self.running:
                logger.warning("🚨 KILL SWITCH DETECTED! Stopping all operations.")
                # In real app, we might want to keep the process alive but stop trading
                # self.running = False
            await asyncio.sleep(5)

    async def stop(self):
        self.running = False
        await self.bot.stop_bot()
        logger.info("Nifty Engine stopped.")

async def main():
    engine = NiftyEngine()
    try:
        await engine.start()
        # Run aggregation and monitoring in parallel
        await asyncio.gather(
            engine.aggregate_candles_loop(),
            engine.monitor_system_loop()
        )
    except asyncio.CancelledError:
        await engine.stop()
    except KeyboardInterrupt:
        await engine.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
