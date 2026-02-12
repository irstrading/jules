# nifty_engine/strategies/base.py

from abc import ABC, abstractmethod
import logging

class BaseStrategy(ABC):
    # Default metadata
    name = "Base Strategy"
    instruments = ["NIFTY"]
    timeframe = "1m"

    def __init__(self):
        self.enabled = False
        self.logger = logging.getLogger(f"Strategy.{self.name}")
        self.symbol = self.instruments[0] if self.instruments else "NIFTY"

    def enable(self):
        self.enabled = True
        self.logger.info(f"Strategy {self.name} enabled")

    def disable(self):
        self.enabled = False
        self.logger.info(f"Strategy {self.name} disabled")

    @abstractmethod
    def on_candle(self, df, context):
        """
        Called when a new candle is formed or updated.
        df: DataFrame containing the latest candles
        context: Object containing market context (Rules, Movers, etc.)
        """
        pass

    def on_option_chain(self, chain, context):
        """
        Optional: Called when new option chain data is available
        """
        pass

    def on_tick(self, tick, context):
        """
        Optional: Called on every tick
        """
        pass

    def send_signal(self, signal_type, price, message=""):
        if self.enabled:
            self.logger.info(f"SIGNAL [{signal_type}] at {price}: {message}")
            return {
                "strategy": self.name,
                "symbol": self.symbol,
                "signal": signal_type,
                "price": price,
                "message": message
            }
        return None
