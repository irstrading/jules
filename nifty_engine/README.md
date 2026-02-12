# 🚀 Nifty Advanced Algo Engine

A modular, professional-grade trading system for the Indian stock market.

## 🏗️ Architecture
- **Core**: Market Engine (Greeks, GEX, OI Sentiment) and Indicators library.
- **Data**: SQLite persistence for 1-minute candles.
- **Ingestor**: Angel One SmartAPI WebSocket integration.
- **Strategies**: Dynamic strategy loading and management.
- **UI**: Streamlit-based live dashboard.
- **Communicator**: Telegram bot for alerts and remote control.

## 🛠️ Setup
1. Install dependencies:
   ```bash
   pip install -r nifty_engine/requirements.txt
   ```
2. Configure your credentials in `nifty_engine/config.py` or set environment variables.

## 🚀 Running the System
1. **Start the Dashboard**:
   ```bash
   streamlit run nifty_engine/ui/app.py
   ```
2. **Start the Engine**:
   ```bash
   python nifty_engine/run_engine.py
   ```

## 📝 Strategy Development
Place your strategy `.py` files in `nifty_engine/strategies/`. Your strategy must inherit from `BaseStrategy`.

```python
from .base import BaseStrategy
from ..core.indicators import Indicators

class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__(name="My Strategy", symbol="NIFTY")

    def on_candle(self, df):
        # Your logic here
        pass
```
