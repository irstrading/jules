# 🔥 Nifty Advanced Algo Engine (OpenAlgo Style)

This is a professional-grade, modular Nifty/Bank Nifty trading engine designed for extreme ease of use. It follows the "OpenAlgo" philosophy: **One-click install, Zero friction.**

---

## ⚡ 3-Minute "Quick Start" (VS Code)

### 1. Open in VS Code
Open the project folder in VS Code.

### 2. Run the Launcher
Open your terminal (`Ctrl + \``) and simply run:
```bash
python launcher.py
```
*The script will automatically install all dependencies and create your `.env` file.*

**For Windows (Single Click):**
Simply double-click `start.bat`. This will run the Engine and Dashboard in a **single terminal window**.

### 3. Fill Your Credentials
Open the newly created `.env` file and paste your Angel One and Telegram details.

### 4. Start Trading
Run `python launcher.py` again, select **Option 1**, and you are live! 🚀

---

## 🛠️ Key Features (The "Impossible" Made Easy)

- **One-Click Setup:** No manual `pip install` or file renaming required.
- **AI-Enhanced Dashboard:** Live 70% Index Alignment, MMI (Market Mood), and ATM Straddle charts.
- **Auto-Token Discovery:** Never worry about weekly expiry changes; the engine handles it.
- **Resilient Connection:** Built-in auto-reconnect with session refresh.
- **Algo Study Center:** Learn GEX, Greeks, and Sentiment directly inside the dashboard.

---

## 📂 Project Structure

- `nifty_engine/`: Core logic, UI, and strategies.
- `launcher.py`: The magical one-click entry point.
- `nifty_data.db`: Your local high-speed persistence layer.
- `.env`: Your secure credentials vault.

---

## 🛡️ Safety First
The system includes a **Global Kill Switch**. If anything goes wrong, hit the Red Button in the dashboard or use your Telegram command to stop all execution instantly.

---

## 🛠️ Troubleshooting

- **ModuleNotFoundError:** If you see this, ensure you run the code via `launcher.py`. It automatically sets the correct `PYTHONPATH` so the internal modules can find each other.
- **Angel One Login:** If your TOTP fails, double-check your `ANGEL_ONE_TOTP_SECRET` in `.env`. It should be the alphanumeric key provided by Angel One during 2FA setup.
- **Windows/PowerShell:** If script execution is disabled on your machine, you might need to run:
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell.

**Happy Trading! Your professional assistant is now ready.**
