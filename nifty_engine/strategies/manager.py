# nifty_engine/strategies/manager.py

import os
import importlib.util
import inspect
from nifty_engine.strategies.base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self, strategies_dir="nifty_engine/strategies"):
        self.strategies_dir = strategies_dir
        self.strategies = {} # {name: instance}

    def load_strategies(self):
        """
        Dynamically loads strategies from the strategies directory.
        """
        for filename in os.listdir(self.strategies_dir):
            if filename.endswith(".py") and filename != "base.py" and filename != "__init__.py" and filename != "manager.py":
                filepath = os.path.join(self.strategies_dir, filename)
                module_name = filename[:-3]

                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                            instance = obj()
                            self.strategies[instance.name] = instance
                            logger.info(f"Loaded strategy: {instance.name}")
                except Exception as e:
                    logger.error(f"Failed to load strategy from {filename}: {e}")

    def get_strategy(self, name):
        return self.strategies.get(name)

    def enable_strategy(self, name):
        if name in self.strategies:
            self.strategies[name].enable()

    def disable_strategy(self, name):
        if name in self.strategies:
            self.strategies[name].disable()

    def run_on_candle(self, symbol, df):
        signals = []
        for name, strategy in self.strategies.items():
            if strategy.enabled and strategy.symbol == symbol:
                signal = strategy.on_candle(df)
                if signal:
                    signals.append(signal)
        return signals

    def stop_all(self):
        for strategy in self.strategies.values():
            strategy.disable()
        logger.info("All strategies stopped.")
