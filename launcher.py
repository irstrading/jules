# launcher.py

import subprocess
import sys
import os
import time
import shutil
import argparse
import venv
from datetime import datetime

# --- Constants ---
VENV_DIR = ".venv"
REQUIREMENTS_FILE = "requirements.txt"
LOGS_DIR = "logs"
DB_DIR = "database"

def print_banner():
    print("\n" + "="*60)
    print("🚀 ANZA OPTION ANALYSIS - PRODUCTION ORCHESTRATOR v4.0 🚀")
    print("============================================================\n")

def create_dirs():
    for d in [LOGS_DIR, DB_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"📁 Created directory: {d}")

def setup_venv():
    """Creates a virtual environment and returns the path to its python executable."""
    if not os.path.exists(VENV_DIR):
        print(f"🐍 Creating virtual environment in {VENV_DIR}...")
        venv.create(VENV_DIR, with_pip=True)
        print("✅ Virtual environment created.")

    # Path to python in venv
    if os.name == "nt": # Windows
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    else: # Linux/Mac
        return os.path.join(VENV_DIR, "bin", "python")

def install_dependencies(python_exe):
    print("📦 Synchronizing dependencies...")
    if os.path.exists(REQUIREMENTS_FILE):
        try:
            # Upgrade pip first
            subprocess.check_call([python_exe, "-m", "pip", "install", "--upgrade", "pip"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Install requirements
            subprocess.check_call([python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
            print("✅ Dependencies are up to date.")
        except Exception as e:
            print(f"❌ Dependency error: {e}")
    else:
        print(f"⚠️ {REQUIREMENTS_FILE} not found. Skipping installation.")

def setup_env():
    if not os.path.exists(".env"):
        print("📝 Configuring environment variables...")
        if os.path.exists(".env.example"):
            shutil.copy(".env.example", ".env")
        else:
            with open(".env", "w") as f:
                f.write("# ANZA PRO CONFIGURATION\n")
                f.write("ANGEL_ONE_API_KEY=YOUR_KEY\n")
                f.write("ANGEL_ONE_CLIENT_CODE=YOUR_CODE\n")
                f.write("ANGEL_ONE_PASSWORD=YOUR_PASS\n")
                f.write("ANGEL_ONE_TOTP_SECRET=YOUR_SECRET\n")
        print("✅ .env initialized. Please update it with your credentials for LIVE trading.")

def run_demo_setup(python_exe):
    print("\n🎮 Initializing High-Fidelity Demo Environment...")
    # Use the venv python to run a mini-script that populates the DB
    cmd = [python_exe, "-c", """
from database.manager import DatabaseManager
from core.simulator import RealisticSimulator
import json, os
from datetime import datetime
db = DatabaseManager()
market_state = RealisticSimulator.generate_market_state()
db.set_config('market_state', json.dumps(market_state))
db.set_config('engine_running', 'ON')
if not os.path.exists('logs'): os.makedirs('logs')
with open('logs/engine.log', 'w') as f:
    f.write(f'{datetime.now()} - INFO - ANZA Engine Started in SIMULATION mode\\n')
    f.write(f'{datetime.now()} - INFO - Connected to Global Market Feed Cluster\\n')
print('✅ Demo data generated successfully.')
"""]
    try:
        subprocess.check_call(cmd)
    except Exception as e:
        print(f"❌ Demo setup failed: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", action="store_true", help="One-click start")
    args = parser.parse_args()

    print_banner()
    create_dirs()
    setup_env()

    python_exe = setup_venv()
    install_dependencies(python_exe)

    if args.auto:
        choice = "1"
    else:
        print("\n[1] Start Full Platform (Recommended)")
        print("[2] Start Dashboard Only")
        print("[3] Start Engine Only")
        print("[4] Reset & Run Demo Setup")
        print("[Q] Quit")
        choice = input("\nSelect Option: ").strip().lower()

    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    procs = []
    try:
        if choice == "1":
            print("\n🚀 Launching Full Institutional Suite...")
            procs.append(subprocess.Popen([python_exe, "main.py"], env=env))
            time.sleep(2) # Give engine time to start
            procs.append(subprocess.Popen([python_exe, "-m", "streamlit", "run", "anza_dashboard.py"], env=env))
        elif choice == "2":
            print("\n📊 Launching Dashboard...")
            procs.append(subprocess.Popen([python_exe, "-m", "streamlit", "run", "anza_dashboard.py"], env=env))
        elif choice == "3":
            print("\n⚙️ Launching Analysis Engine...")
            procs.append(subprocess.Popen([python_exe, "main.py"], env=env))
        elif choice == "4":
            run_demo_setup(python_exe)
            print("\n💡 Demo mode ready. Now select Option 1 to view the results.")
            return
        elif choice == "q":
            return
        else:
            print("❌ Invalid choice.")
            return

        print("\n✅ System is running. Press CTRL+C to stop all processes.")

        # Keep launcher alive
        while True:
            time.sleep(5)
            # Check if any process died
            for p in procs:
                if p.poll() is not None:
                    print(f"\n⚠️ A system process (PID {p.pid}) has stopped.")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down ANZA PRO...")
        for p in procs:
            p.terminate()
            try:
                p.wait(timeout=5)
            except:
                p.kill()
        print("✅ Clean shutdown complete.")

if __name__ == "__main__":
    main()
