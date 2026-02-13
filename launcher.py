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
    if os.path.exists("requirements.txt"):
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
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
            with open(".env", "w") as f:
                f.write("ANGEL_ONE_API_KEY=\nANGEL_ONE_CLIENT_CODE=\nANGEL_ONE_PASSWORD=\nANGEL_ONE_TOTP_SECRET=\n")
            print("✅ .env created. PLEASE FILL YOUR CREDENTIALS IN .env FILE!")

def create_dirs():
    dirs = ["logs", "database", "scripts"]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

def start_engine():
    print("🚀 Starting ANZA Analysis Engine...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}{os.pathsep}{env.get('PYTHONPATH', '')}"
    return subprocess.Popen([sys.executable, "main.py"], env=env)

def start_dashboard():
    print("📊 Starting ANZA Institutional Dashboard...")
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{os.getcwd()}{os.pathsep}{env.get('PYTHONPATH', '')}"
    ui_path = "anza_dashboard.py"
    return subprocess.Popen([sys.executable, "-m", "streamlit", "run", ui_path], env=env)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="Auto-start Engine and Dashboard")
    args, unknown = parser.parse_known_args()

    print("=========================================")
    print("💎 ANZA OPTION ANALYSIS - MASTER ENGINE 💎")
    print(f"🐍 Environment: Python {sys.version.split()[0]}")
    print("=========================================")

    create_dirs()
    install_dependencies()
    setup_env_file()

    if args.auto:
        print("\n🤖 AUTO-START MODE ACTIVATED")
        processes = [start_engine(), start_dashboard()]
    else:
        print("\n1. Start Full Platform")
        print("2. Start Engine Only")
        print("3. Start Dashboard Only")
        print("4. Run Demo Setup (Populate Mock Data)")
        print("q. Quit")

        choice = input("\nEnter choice: ").strip().lower()
        processes = []
        if choice == '1':
            processes.extend([start_engine(), start_dashboard()])
        elif choice == '2':
            processes.append(start_engine())
        elif choice == '3':
            processes.append(start_dashboard())
        elif choice == '4':
            run_demo_setup()
            sys.exit(0)
        elif choice == 'q':
            sys.exit(0)

def run_demo_setup():
    print("\n🎮 Setting up Demo Mode...")
    try:
        from database.manager import DatabaseManager
        import pandas as pd
        import numpy as np
        import json

        db = DatabaseManager()
        # 1. Create fake market state
        market_state = {
            "alignment": {"bullish_pct": 85.0, "bearish_pct": 15.0, "status": "Strong Bullish Trend"},
            "stock_states": {"RELIANCE": {"lp": 2505, "pc": 2480}},
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        db.set_config("market_state", json.dumps(market_state))
        db.set_config("engine_running", "ON")
        print("✅ Demo data populated.")
    except Exception as e:
        print(f"❌ Demo setup failed: {e}")

    try:
        while True:
            time.sleep(1)
            for p in processes:
                if p.poll() is not None:
                    print(f"⚠️ Process {p.pid} stopped.")
                    break
    except KeyboardInterrupt:
        print("\n🛑 Stopping ANZA...")
        for p in processes: p.terminate()

if __name__ == "__main__":
    main()
