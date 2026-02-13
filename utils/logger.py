# utils/logger.py

import logging
import os

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/engine.log"),
            logging.StreamHandler()
        ]
    )
