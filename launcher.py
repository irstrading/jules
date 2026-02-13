# launcher.py

import subprocess
import sys
import os
import time
import shutil
import argparse
from datetime import datetime

def install_dependencies():
    print("📦 Checking & Installing Dependencies...")
    req_path = os.path.join("nifty_engine", "requirements.txt")
    if os.path.exists(req_path):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])
            print("✅ Dependencies ready.")
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
    else:
        print("⚠️ requirements.txt not found.")

def setup_env_file():
    if not os.path.exists(".env"):
        print("📝 Creating .env from example...")
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
            print("✅ .env created. PLEASE FILL YOUR CREDENTIALS IN .env FILE!")
        else:
            print("❌ .env.example not found. Cannot create .env.")
    else:
        print("✅ .env file detected.")

def create_dirs():
    dirs = ["nifty_engine/logs", "nifty_engine/strategies", "nifty_engine/data"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"📁 Created directory: {d}")

# Delayed import to ensure dependencies are installed first
def get_config_safely():
    try:
        from nifty_engine.config import (
            validate_config, ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_CODE,
            ANGEL_ONE_PASSWORD, ANGEL_ONE_TOTP_SECRET, TELEGRAM_BOT_TOKEN
        )
        return {
            "valid": validate_config(),
            "api_key": ANGEL_ONE_API_KEY,
            "client_code": ANGEL_ONE_CLIENT_CODE,
            "tg_token": TELEGRAM_BOT_TOKEN
        }
    except ImportError:
        return None

def is_market_open():
    try:
        import pytz
    except ImportError:
        return False, "pytz not installed"

    tz = pytz.timezone('Asia/Kolkata')
    """Checks if Indian Market is currently open (09:15 - 15:30 IST)"""
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)

    # Monday = 0, Sunday = 6
    if now.weekday() >= 5:
        return False, "Weekend"

    start_time = now.replace(hour=9, minute=15, second=0, microsecond=0)
    end_time = now.replace(hour=15, minute=30, second=0, microsecond=0)

    if start_time <= now <= end_time:
        return True, "Open"
    elif now < start_time:
        return False, f"Market opens at 09:15 AM (Current: {now.strftime('%H:%M')})"
    else:
        return False, "Market is closed for the day"

def check_readiness():
    print("\n🔍 Running System Readiness Check...")

    config = get_config_safely()
    if not config:
        print("❌ Critical: Could not load configuration. Ensure dependencies are installed.")
        return False

    ready = True

    # 1. Config Validation
    if config["valid"]:
        print("✅ Configuration: VALID")
    else:
        print("❌ Configuration: INVALID (Check your .env file)")
        ready = False

    # 2. Market Hours
    is_open, status = is_market_open()
    if is_open:
        print(f"✅ Market Status: OPEN")
    else:
        print(f"⚠️ Market Status: CLOSED ({status})")

    # 3. Telegram Token Check
    if config["tg_token"] and ":" in config["tg_token"]:
        print("✅ Telegram Token: FORMAT VALID")
    else:
        print("❌ Telegram Token: MISSING or INVALID")
        ready = False

    if ready:
        print("\n🚀 SYSTEM READY ✅")
    else:
        print("\n🛑 FIX ERRORS ABOVE IN .env FILE ❌")

    return ready

def start_engine():
    print("🚀 Starting Nifty Engine...")
    env = os.environ.copy()
    # Cross-platform PYTHONPATH separator
    current_pp = env.get('PYTHONPATH', '')
    if current_pp:
        env["PYTHONPATH"] = f"{os.getcwd()}{os.pathsep}{current_pp}"
    else:
        env["PYTHONPATH"] = os.getcwd()
    return subprocess.Popen([sys.executable, "nifty_engine/run_engine.py"], env=env)

def start_dashboard():
    print("📊 Starting Streamlit Dashboard...")
    # Add PYTHONPATH so streamlit can find nifty_engine
    env = os.environ.copy()
    current_pp = env.get('PYTHONPATH', '')
    if current_pp:
        env["PYTHONPATH"] = f"{os.getcwd()}{os.pathsep}{current_pp}"
    else:
        env["PYTHONPATH"] = os.getcwd()
    # Use 'python -m streamlit' to ensure we use the streamlit associated with sys.executable
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", "nifty_engine/ui/app.py"], env=env)

def run_demo_setup():
    print("\n🎮 Setting up Demo Mode...")
    try:
        from nifty_engine.data.database import Database
        import pandas as pd
        import numpy as np
        import json

        db = Database()
        # 1. Create fake candles
        timestamps = pd.date_range(end=datetime.now(), periods=100, freq='1min')
        prices = [24500 + (np.sin(i/10)*50) + (np.random.randn()*5) for i in range(100)]
        df = pd.DataFrame({'timestamp': timestamps, 'open': prices, 'high': prices, 'low': prices, 'close': prices, 'volume': 1000})
        db.save_candles(df, "NIFTY")

        # 2. Create fake market state
        market_state = {
            "alignment": {"bullish_pct": 75.0, "bearish_pct": 20.0, "status": "Strong Bullish Trend (70%+ Aligned)"},
            "stock_states": {"RELIANCE": {"lp": 2505, "pc": 2480}, "HDFCBANK": {"lp": 1610, "pc": 1590}},
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db.set_config("market_state", json.dumps(market_state))
        db.set_config("engine_running", "ON")

        print("✅ Demo data populated. You can now start the Dashboard (Option 3).")
    except Exception as e:
        print(f"❌ Demo setup failed: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Auto-start Engine and Dashboard")
    args, unknown = parser.parse_known_args()

    print("=========================================")
    print("🔥 Nifty Advanced Algo Engine Launcher 🔥")
    print(f"🐍 Environment: Python {sys.version.split()[0]}")
    print("=========================================")

    # Auto Setup
    create_dirs()
    install_dependencies()
    setup_env_file()

    is_ready = check_readiness()

    if args.auto:
        print("\n🤖 AUTO-START MODE ACTIVATED")
        choice = '1'
    else:
        print("\n1. Start Engine & Dashboard (Full Production Mode)")
        print("2. Start Engine Only")
        print("3. Start Dashboard Only")
        print("4. Run Demo Mode Setup (Populate Mock Data)")
        print("q. Quit")

        choice = input("\nEnter your choice: ").strip().lower()

    processes = []

    if choice == '1':
        processes.append(start_engine())
        time.sleep(2)
        processes.append(start_dashboard())
    elif choice == '2':
        processes.append(start_engine())
    elif choice == '3':
        processes.append(start_dashboard())
    elif choice == '4':
        run_demo_setup()
        sys.exit(0)
    elif choice == 'q':
        sys.exit(0)
    else:
        print("Invalid choice.")
        sys.exit(1)

    print("\n✅ Running... Press Ctrl+C to stop all processes.")

    try:
        while True:
            time.sleep(1)
            # Check if processes are still running
            for p in processes:
                if p.poll() is not None:
                    print(f"⚠️ Process {p.pid} has stopped.")
                    break
    except KeyboardInterrupt:
        print("\n🛑 Stopping all processes...")
        for p in processes:
            p.terminate()
        print("Done.")

if __name__ == "__main__":
    main()
