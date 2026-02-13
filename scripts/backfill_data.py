# scripts/backfill_data.py

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backfill():
    print("🔄 Backfilling historical data (Last 5 Days)...")
    # In real use, this would fetch from Angel One getCandleData
    print("✅ Backfill simulation complete.")

if __name__ == "__main__":
    backfill()
