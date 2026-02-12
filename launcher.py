# launcher.py

import subprocess
import sys
import os
import time
from datetime import datetime
import pytz
from nifty_engine.config import (
    validate_config, ANGEL_ONE_API_KEY, ANGEL_ONE_CLIENT_CODE,
    ANGEL_ONE_PASSWORD, ANGEL_ONE_TOTP_SECRET, TELEGRAM_BOT_TOKEN
)

def is_market_open():
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
    ready = True

    # 1. Config Validation
    if validate_config():
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
        # We don't block start just because market is closed (for testing)

    # 3. Database Check
    if os.path.exists("nifty_data.db"):
        print("✅ Database: FOUND")
    else:
        print("⚠️ Database: NOT FOUND (Will be created on start)")

    # 4. Telegram Token Check
    if TELEGRAM_BOT_TOKEN and ":" in TELEGRAM_BOT_TOKEN:
        print("✅ Telegram Token: FORMAT VALID")
    else:
        print("❌ Telegram Token: MISSING or INVALID")
        ready = False

    if ready:
        print("\n🚀 SYSTEM READY ✅")
    else:
        print("\n🛑 FIX ERRORS ABOVE BEFORE STARTING ❌")

    return ready

def start_engine():
    print("🚀 Starting Nifty Engine...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"
    return subprocess.Popen([sys.executable, "nifty_engine/run_engine.py"], env=env)

def start_dashboard():
    print("📊 Starting Streamlit Dashboard...")
    # Add PYTHONPATH so streamlit can find nifty_engine
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"
    return subprocess.Popen(["streamlit", "run", "nifty_engine/ui/app.py"], env=env)

def main():
    print("=========================================")
    print("🔥 Nifty Advanced Algo Engine Launcher 🔥")
    print("=========================================")

    is_ready = check_readiness()

    print("\n1. Start Engine & Dashboard (Full Production Mode)")
    print("2. Start Engine Only")
    print("3. Start Dashboard Only")
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
