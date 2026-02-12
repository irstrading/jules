# 🚀 Nifty Advanced Algo Engine

This is a modular, professional-grade trading system for the Indian stock market (Nifty focus).

## ✨ Key Features

- **Modular 3-Layer Architecture**: Ingestor (WebSockets), Brain (Analysis Engine), and Communicator (Telegram/UI).
- **Advanced Market Engine**: Built-in support for Option Greeks (Black-Scholes), Gamma Exposure (GEX), and Smart Money OI Sentiment analysis.
- **Indicators Library**: Pre-built SMA, EMA, VWAP, RSI, Stochastic RSI, MACD, and ADX.
- **Dynamic Strategy Management**: Upload and toggle Python-based strategies through the UI.
- **Real-time Dashboard**: Streamlit-based interface for live market data and strategy monitoring.
- **Telegram Integration**: Receive signals and control the engine remotely via Telegram.
- **Safety First**: Global emergency stop (Kill Switch) both in the UI and via Telegram.

## 📁 Project Structure

- `nifty_engine/core/`: Market calculations and technical indicators.
- `nifty_engine/data/`: Database management and historical data patching.
- `nifty_engine/strategies/`: Folder for custom trading strategies.
- `nifty_engine/ui/`: Streamlit dashboard code.
- `nifty_engine/communicator/`: Telegram bot integration.

## 🚀 Quick Start

For detailed instructions, see the [Nifty Engine README](nifty_engine/README.md).

1. Install requirements: `pip install -r nifty_engine/requirements.txt`
2. Configure `nifty_engine/config.py`.
3. Launch the dashboard: `streamlit run nifty_engine/ui/app.py`
4. Start the engine: `python nifty_engine/run_engine.py`

---
*Inspired by OpenAlgo. Built for precision trading.*
