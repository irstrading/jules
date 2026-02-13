# services/alert_service.py

import logging

logger = logging.getLogger(__name__)

class AlertService:
    async def send_signals(self, signals):
        for s in signals:
            logger.info(f"🚨 SIGNAL ALERT: {s['strategy']} - {s['direction']} at {s['entry']}")
