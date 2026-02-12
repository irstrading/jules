# launcher.py

import subprocess
import sys
import os
import time
from nifty_engine.config import validate_config

def start_engine():
    print("🚀 Starting Nifty Engine...")
    return subprocess.Popen([sys.executable, "nifty_engine/run_engine.py"])

def start_dashboard():
    print("📊 Starting Streamlit Dashboard...")
    return subprocess.Popen(["streamlit", "run", "nifty_engine/ui/app.py"])

def main():
    print("=========================================")
    print("🔥 Nifty Advanced Algo Engine Launcher 🔥")
    print("=========================================")

    if not validate_config():
        sys.exit(1)

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
