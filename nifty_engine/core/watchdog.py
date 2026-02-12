# nifty_engine/core/watchdog.py

import time
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ConnectionWatchdog:
    def __init__(self, timeout_seconds=60):
        self.timeout_seconds = timeout_seconds
        self.last_tick_time = datetime.now()
        self.is_connected = False

    def notify_tick(self):
        self.last_tick_time = datetime.now()
        self.is_connected = True

    def check_connection(self):
        """Returns True if connection is healthy, False if timed out."""
        elapsed = (datetime.now() - self.last_tick_time).total_seconds()
        if elapsed > self.timeout_seconds:
            self.is_connected = False
            return False
        return True

    def reset(self):
        self.last_tick_time = datetime.now()
        self.is_connected = True

class AutoReconnect:
    def __init__(self, ingestor, max_retries=5):
        self.ingestor = ingestor
        self.max_retries = max_retries
        self.retry_count = 0

    def attempt_reconnect(self):
        logger.warning(f"Attempting Reconnection... (Attempt {self.retry_count + 1}/{self.max_retries})")
        if self.ingestor.login():
            logger.info("Re-login successful. Restarting WebSocket...")
            # Note: Re-subscription logic should be handled by the caller or Ingestor
            self.retry_count = 0
            return True
        else:
            self.retry_count += 1
            return False

    def should_retry(self):
        return self.retry_count < self.max_retries
