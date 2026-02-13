# scripts/setup_database.py

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.manager import DatabaseManager

def setup():
    print("🛠️ Initializing ANZA Database...")
    db = DatabaseManager()
    if db.test_connection():
        print("✅ Database initialized successfully.")
    else:
        print("❌ Database initialization failed.")

if __name__ == "__main__":
    setup()
