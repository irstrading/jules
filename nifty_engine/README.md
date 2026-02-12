# 🚀 Nifty Advanced Algo Engine

## 🛠️ Setup & Security
1.  **Environment Variables**: All sensitive data (API keys, passwords) must be stored in the root `.env` file. Never hardcode them in `config.py`.
2.  **Launcher**: Use `python launcher.py` from the root directory to manage the system.

## 📁 Modular Components
- `core/`: High-performance calculations.
- `data/`: SQLite persistence layer.
- `strategies/`: Dynamic loading zone. Add your `.py` files here.
- `ui/`: Streamlit dashboard.
- `communicator/`: Telegram bot for remote management.

## 🛡️ Safety Mechanisms
- **Emergency Stop**: The "RED BUTTON" in the dashboard and `/stop` command in Telegram will instantly disable all strategies.
- **Validation**: `config.py` validates that all required credentials are present before allowing the system to start.

---
*Production Ready | Modular | Secure*
