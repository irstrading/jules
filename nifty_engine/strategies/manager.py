# nifty_engine/strategies/manager.py

import os
import importlib.util
import inspect
from nifty_engine.strategies.base import BaseStrategy
import logging

logger = logging.getLogger(__name__)

class StrategyManager:
    def __init__(self, db, strategies_dir="nifty_engine/strategies"):
        self.db = db
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
            self.db.set_config(f"strategy_{name}", "ON")

    def disable_strategy(self, name):
        if name in self.strategies:
            self.strategies[name].disable()
            self.db.set_config(f"strategy_{name}", "OFF")

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
            self.db.set_config(f"strategy_{strategy.name}", "OFF")
        self.db.set_config("kill_switch", "ON")
        logger.info("All strategies stopped and Kill Switch activated.")

    def sync_with_db(self):
        """Syncs the enabled status of strategies with the database"""
        kill_switch = self.db.get_config("kill_switch", "OFF")
        for name, strategy in self.strategies.items():
            if kill_switch == "ON":
                strategy.disable()
            else:
                status = self.db.get_config(f"strategy_{name}", "OFF")
                if status == "ON" and not strategy.enabled:
                    strategy.enable()
                elif status == "OFF" and strategy.enabled:
                    strategy.disable()
