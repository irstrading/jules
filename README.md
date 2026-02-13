# 🚀 OpenAlgo Nifty v3: Advanced Dream Assistant

Welcome to your professional-grade Nifty/Bank Nifty trading engine. This system is designed for **VS Code** and follows the modular "OpenAlgo" architecture.

---

## 🛠️ Step-by-Step Installation Guide (VS Code)

### 1. Open Project in VS Code
- Open VS Code.
- Go to `File > Open Folder...` and select the directory containing this project.

### 2. Set Up Python Environment
Open the VS Code Terminal (`Ctrl + \`` or `Terminal > New Terminal`) and run:
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
Run the following command to install all necessary libraries:
```bash
pip install -r nifty_engine/requirements.txt
```

### 4. Configure Your Credentials
1. Look for the `.env.example` file in the root directory.
2. **Rename it** to `.env`.
3. Fill in your Angel One credentials:
   - `ANGEL_ONE_CLIENT_CODE`: Your User ID.
   - `ANGEL_ONE_PASSWORD`: Your login password.
   - `ANGEL_ONE_API_KEY`: Your App API Key.
   - `ANGEL_ONE_TOTP_SECRET`: Your 32-digit TOTP seed.
   - `TELEGRAM_BOT_TOKEN`: Your bot token from @BotFather.
   - `TELEGRAM_CHAT_ID`: Your personal Chat ID.

### 5. Launch the System
Run the centralized launcher script:
```bash
python launcher.py
```
- **Option 1:** Starts both the Engine (Live Data) and the Dashboard.
- **Option 2:** Starts only the Engine (Low resource mode).
- **Option 3:** Starts only the Dashboard (To view historical data).

---

## 📊 How to Access & Learn

### 🌐 Accessing the Dashboard
Once launched, VS Code will show a link: `http://localhost:8501`.
- Hold `Ctrl` and click the link to open your professional trading terminal in your browser.

### 🧠 The Algo Study Center
To understand the complex data (GEX, MMI, 70% Rule):
1. Open the Dashboard.
2. Select **"Algo Study Center"** from the left sidebar.
3. This is your built-in textbook explaining all advanced concepts.

### 🤖 AI Market Interpretation
Check the **"AI Market Interpretation"** box on the main Dashboard. It automatically reads the live market data and tells you the "story" of the current trend in plain English.

---

## ⚠️ Safety Mechanism: The Kill Switch
- **Emergency Stop:** Press the large red button on the Dashboard sidebar to immediately stop all logic and disconnect.
- **Reset:** To resume, you must click "Reset Kill Switch" in the sidebar.

---

## 🛡️ Production Readiness Checklist
- [ ] `.env` file renamed and filled.
- [ ] Internet connection is stable.
- [ ] `scrip_master.json` will auto-download on first run.
- [ ] Market is open (09:15 AM - 03:30 PM).

**Happy Trading! Your assistant is now ready.**
