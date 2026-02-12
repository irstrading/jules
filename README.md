# 🚀 Nifty Advanced Algo Engine

This is a modular, professional-grade trading system for the Indian stock market (Nifty focus).

## ✨ Key Features

- **Modular 3-Layer Architecture**: Ingestor (WebSockets), Brain (Analysis Engine), and Communicator (Telegram/UI).
- **Shared-State Synchronization**: Uses a SQLite backend to sync strategy status and a global **Kill Switch** between the Engine, Dashboard, and Telegram Bot.
- **Advanced Market Engine**: Built-in support for Option Greeks (Black-Scholes), Gamma Exposure (GEX), and Smart Money OI Sentiment analysis.
- **Indicators Library**: Pre-built SMA, EMA, VWAP, RSI, Stochastic RSI, MACD, and ADX.
- **Dynamic Strategy Management**: Upload and toggle Python-based strategies through the UI.
- **Real-time Dashboard**: Streamlit-based interface for live market data and strategy monitoring.
- **Telegram Integration**: Receive signals and control the engine remotely via Telegram.
- **Safety First**: Global emergency stop (Kill Switch) that instantly halts all trading processes.

## 📁 Project Structure

- `nifty_engine/core/`: Market calculations and technical indicators.
- `nifty_engine/data/`: Database management and shared state persistence.
- `nifty_engine/strategies/`: Folder for custom trading strategies.
- `nifty_engine/ui/`: Streamlit dashboard code.
- `nifty_engine/communicator/`: Telegram bot integration.
- `launcher.py`: Unified launcher for the whole system.

## 🔌 Plug and Play Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r nifty_engine/requirements.txt
    ```
2.  **Configure Credentials**:
    - Copy `.env.example` to `.env`: `cp .env.example .env`
    - Open `.env` and enter your Angel One API Key, Client Code, Password, and TOTP Secret.
    - (Optional) Enter your Telegram Bot Token and Chat ID for mobile alerts.
3.  **Launch the System**:
    ```bash
    python launcher.py
    ```
    Follow the interactive menu to start the Engine, the Dashboard, or both!

## 🛡️ Production Safety
- **Kill Switch**: If you trigger the "EMERGENCY STOP" in the UI or `/stop` in Telegram, the Engine process will detect the flag within seconds and halt all strategy executions.
- **Persistence**: All signals and market candles are saved to `nifty_data.db`, allowing you to restart the system without losing history.

---
*Inspired by OpenAlgo. Built for precision trading.*
