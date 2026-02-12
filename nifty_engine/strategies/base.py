# nifty_engine/strategies/base.py

from abc import ABC, abstractmethod
import logging

class BaseStrategy(ABC):
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol
        self.enabled = False
        self.logger = logging.getLogger(f"Strategy.{name}")

    def enable(self):
        self.enabled = True
        self.logger.info(f"Strategy {self.name} enabled for {self.symbol}")

    def disable(self):
        self.enabled = False
        self.logger.info(f"Strategy {self.name} disabled")

    @abstractmethod
    def on_candle(self, df):
        """
        Called when a new candle is formed or updated.
        df: DataFrame containing the latest candles
        """
        pass

    def on_tick(self, tick):
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
