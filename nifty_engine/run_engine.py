# nifty_engine/run_engine.py

import asyncio
import logging
from nifty_engine.core.ingestor import AngelOneIngestor
from nifty_engine.data.database import Database
from nifty_engine.strategies.manager import StrategyManager
from nifty_engine.communicator.telegram_bot import TelegramBot
from nifty_engine.config import NIFTY_SYMBOL
from nifty_engine.core.watchdog import ConnectionWatchdog, AutoReconnect
from nifty_engine.core.movers import NiftyMovers
from nifty_engine.core.rules_engine import RulesEngine
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
        self.watchdog = ConnectionWatchdog(timeout_seconds=30)
        self.reconnector = AutoReconnect(self.ingestor)
        self.movers = NiftyMovers()
        self.rules_engine = RulesEngine()
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
        if self.ingestor.login():
            self.ingestor.set_on_tick_callback(self.on_tick)

            # 4. Warm-up: Fetch last 5 days of 1-minute candles
            to_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            from_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M')
            logger.info(f"Warming up indicators from {from_date} to {to_date}...")

            hist_data = self.ingestor.fetch_historical_data("99926000", "NSE", "ONE_MINUTE", from_date, to_date)
            if hist_data:
                df_hist = pd.DataFrame(hist_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                self.db.save_candles(df_hist, NIFTY_SYMBOL)
                logger.info("Warm-up complete.")

            # 5. Connect WebSocket
            # Token '99926000' for NIFTY Index on NSE
            self.ingestor.connect_websocket("nifty_feed", 1, 1, [{"exchangeType": 1, "tokens": ["99926000"]}])
        else:
            logger.error("Failed to login to Angel One. System running in OFFLINE mode.")

        self.running = True
        logger.info("Nifty Engine is now running!")

    def on_tick(self, tick):
        """Callback for live ticks"""
        self.watchdog.notify_tick()

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

        # Prepare Context for Strategies
        context = {
            "dynamic_rules": self.rules_engine.get_dynamic_context(),
            "movers": self.movers.weights, # Static weights for now
            "timestamp": datetime.now()
        }

        # Fetch last candles for technical analysis
        history_df = self.db.get_last_candles(symbol, limit=100)

        # Run strategies
        signals = self.strategy_manager.run_on_candle(symbol, history_df, context=context)

        # Handle signals
        for signal in signals:
            self.db.log_alert(signal['symbol'], signal['message'], signal['strategy'])
            asyncio.create_task(self.bot.send_alert(f"[{signal['strategy']}] {signal['symbol']}: {signal['message']} at {signal['price']}"))

    async def monitor_system_loop(self):
        """Monitor for Kill Switch, Connection Health, and Strategy updates"""
        while self.running:
            # 1. Sync Strategies
            self.strategy_manager.sync_with_db()

            # 2. Check Connection
            if not self.watchdog.check_connection():
                logger.error("📡 Connection Timeout Detected!")
                await self.bot.send_alert("⚠️ Connection Timeout! Attempting auto-reconnect...")
                if self.reconnector.should_retry():
                    if self.reconnector.attempt_reconnect():
                        self.watchdog.reset()
                        await self.bot.send_alert("✅ Connection Restored.")
                else:
                    logger.critical("❌ Max Reconnection Retries Reached!")
                    await self.bot.send_alert("🛑 Critical Failure: Reconnection failed multiple times.")

            # 3. Check Kill Switch
            if self.db.get_config("kill_switch") == "ON":
                logger.warning("🚨 KILL SWITCH ACTIVE!")

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
