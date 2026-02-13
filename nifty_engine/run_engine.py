# nifty_engine/run_engine.py

import asyncio
import logging
import json
import threading
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

# Configure logging to both file and console
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Console Handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

# File Handler
if not os.path.exists("nifty_engine/logs"):
    os.makedirs("nifty_engine/logs")
file_handler = logging.FileHandler("nifty_engine/logs/engine.log")
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

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
        self.tick_lock = threading.Lock()
        self.stock_states = {} # {symbol: {'lp': price, 'pc': close}}
        self.atm_strike = None
        self.straddle_tokens = [] # [ce_token, pe_token]

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
            # Token '99926000' for NIFTY, '99926009' for BANKNIFTY, '99919017' for SENSEX
            tokens = [
                {"exchangeType": 1, "tokens": ["99926000", "99926009"]}, # NSE
                {"exchangeType": 3, "tokens": ["99919017"]} # BSE for Sensex
            ]
            tokens.extend(self.movers.get_token_list())

            self.ingestor.connect_websocket("nifty_feed", 1, 1, tokens)
        else:
            logger.error("Failed to login to Angel One. System running in OFFLINE mode.")

        self.running = True
        logger.info("Nifty Engine is now running!")

    def on_tick(self, tick):
        """Callback for live ticks"""
        self.watchdog.notify_tick()

        if self.db.get_config("kill_switch") == "ON":
            return

        token = tick.get('tk')
        lp = float(tick.get('lp', 0))

        if token == "99926000":
            # NIFTY Index tick
            with self.tick_lock:
                self.tick_data.append({
                    'symbol': 'NIFTY',
                    'timestamp': datetime.now(),
                    'price': lp,
                    'volume': int(tick.get('v', 0))
                })
            # Discover ATM if not set
            if self.atm_strike is None or datetime.now().minute % 15 == 0:
                new_atm = self.ingestor.get_atm_strike(lp)
                if new_atm != self.atm_strike:
                    self.atm_strike = new_atm
                    logger.info(f"New ATM Strike Discovered: {self.atm_strike}")
                    # In real app, we'd find tokens and subscribe here

        elif token in ["99926009", "99919017"]:
            # Other Indices
            with self.tick_lock:
                self.tick_data.append({
                    'symbol': 'BANKNIFTY' if token == "99926009" else 'SENSEX',
                    'timestamp': datetime.now(),
                    'price': lp,
                    'volume': int(tick.get('v', 0))
                })
        elif token in self.movers.token_to_symbol:
            # Stock tick
            symbol = self.movers.token_to_symbol[token]
            # In production, 'pc' (prev close) is needed for direction
            # For simplicity, we compare with the first seen price if pc is missing
            if symbol not in self.stock_states:
                self.stock_states[symbol] = {'lp': lp, 'pc': lp} # Mock pc for first tick
            else:
                self.stock_states[symbol]['lp'] = lp

    async def aggregate_candles_loop(self):
        """Background loop to aggregate ticks into 1-minute candles for all indices"""
        while self.running:
            # Align with clock minutes (e.g., run at 10:01:00.100)
            now = datetime.now()
            sleep_time = 60 - now.second - (now.microsecond / 1_000_000.0) + 0.1
            await asyncio.sleep(sleep_time)

            with self.tick_lock:
                if not self.tick_data:
                    continue
                ticks_to_process = list(self.tick_data)
                self.tick_data = [] # Clear buffer

            df_all_ticks = pd.DataFrame(ticks_to_process)

            for symbol in df_all_ticks['symbol'].unique():
                df_ticks = df_all_ticks[df_all_ticks['symbol'] == symbol]

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
                self.on_candle_closed(symbol, df_candle)

    def on_candle_closed(self, symbol, candle_df):
        # Save to DB
        self.db.save_candles(candle_df, symbol)

        # Sync strategy status from DB before running
        self.strategy_manager.sync_with_db()

        # Calculate Stock Directions for 70% Alignment
        stock_directions = {}
        for symbol, state in self.stock_states.items():
            if state['lp'] > state['pc']:
                stock_directions[symbol] = 1
            elif state['lp'] < state['pc']:
                stock_directions[symbol] = -1
            else:
                stock_directions[symbol] = 0

        from nifty_engine.core.market_engine import IndexAlignment
        alignment = IndexAlignment.calculate(stock_directions, self.movers.weights)

        # Save Market State for UI
        market_state = {
            "alignment": alignment,
            "stock_states": self.stock_states,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.db.set_config("market_state", json.dumps(market_state))

        # Prepare Context for Strategies
        context = {
            "dynamic_rules": self.rules_engine.get_dynamic_context(),
            "movers": self.movers.weights,
            "stock_directions": stock_directions,
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
                        # Restart WebSocket
                        self.ingestor.connect_websocket("nifty_feed", 1, 1, [{"exchangeType": 1, "tokens": ["99926000"]}])
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
