# 🚀 ANZA OPTION ANALYSIS - Institutional Master Platform

A professional-grade, modular Nifty/Bank Nifty and Stock Option analysis engine designed for elite traders. Built with institutional-level logic: Greeks, GEX, Smart Money Tracking, and AI-driven market narratives.

---

## ⚡ 3-Minute "Quick Start" (VS Code)

### 1. Open in VS Code
Open the project folder in VS Code.

### 2. Run the Platform
**Windows (Recommended):**
Simply double-click **`start.bat`**. This will:
1.  Auto-install all required libraries.
2.  Create your secure `.env` credentials file.
3.  Launch both the **Analysis Engine** and **Institutional Dashboard** in a single window.

**Other OS:**
Run `python launcher.py --auto` in your terminal.

### 3. Fill Your Credentials
Open the newly created `.env` file and paste your Angel One and Telegram details.

### 4. Start Trading
Run `start.bat` again, select **Option 1**, and you are live! 🚀
*(Or select **Option 4** to see the system with demo data immediately!)*

---

## 🛠️ Key Features

- **Institutional Logic:** Real-time Greeks, GEX, and MMI tracking.
- **Smart Money Tracking:** Automated analysis of FII/DII/Retail positioning.
- **Behavior Tagging:** Automatic identification of Long Buildup, Short Covering, etc.
- **Self-Learning Engine:** Tracks outcomes and adjusts confidence scores.
- **Institutional Playbook:** Built-in library of 190+ professional trading patterns.

---

## 📂 Project Structure

- `main.py`: Orchestrator of the analysis cycles.
- `anza_dashboard.py`: Premium institutional dashboard.
- `core/`: Advanced analysis engines (Greeks, GEX, OI).
- `services/`: API wrappers (Angel One, Alerts).
- `database/`: Persistence layer and Knowledge Base.
- `logs/`: Real-time system logs.

---

## 🛡️ Safety First
The system includes a **Global Circuit Breaker**. If data quality drops or an API error occurs, the system halts trading and alerts you instantly.

---

## 🛠️ Troubleshooting

- **ModuleNotFoundError:** Ensure you run the code via `launcher.py` or `start.bat`.
- **Angel One Login:** Double-check your `ANGEL_ONE_TOTP_SECRET` in `.env`.
- **Windows/PowerShell:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` if scripts are disabled.

**Happy Trading! Your institutional assistant is now ready.**
