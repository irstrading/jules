# nifty_engine/utils/export_knowledge.py

import json
import os
from datetime import datetime

def export_to_text():
    kb_path = "nifty_engine/data/knowledge_base.json"
    output_path = "Institutional_Knowledge_Master.txt"

    if not os.path.exists(kb_path):
        print("Knowledge base not found.")
        return

    with open(kb_path, 'r') as f:
        kb = json.load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("====================================================\n")
        f.write("🔥 INSTITUTIONAL TRADING KNOWLEDGE MASTER FILE 🔥\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("====================================================\n\n")

        f.write("1. MARKET STRUCTURE & WEIGHTS\n")
        f.write("-----------------------------\n")
        for symbol, data in kb.get("nifty_50_weights", {}).items():
            f.write(f"• {symbol}: {data['weight']}% weight (Token: {data['token']})\n")
        f.write("\n")

        f.write("2. INSTITUTIONAL PATTERN PLAYBOOK\n")
        f.write("---------------------------------\n")
        patterns = kb.get("institutional_patterns", {})
        for cat, items in patterns.items():
            f.write(f"\n[{cat.upper().replace('_', ' ')}]\n")
            for name, p in items.items():
                f.write(f"\n>>> PATTERN: {name.replace('_', ' ').title()}\n")
                f.write(f"    - Detection: {p['detection']}\n")
                f.write(f"    - Meaning: {p['meaning']}\n")
                f.write(f"    - Action: {p['action']}\n")
                if 'historical_success' in p:
                    f.write(f"    - Historical Success: {p['historical_success']}\n")
                if 'risk' in p:
                    f.write(f"    - Risk: {p['risk']}\n")
        f.write("\n")

        f.write("3. MASTER TRADING RULES\n")
        f.write("-----------------------\n")
        for rule, desc in kb.get("trading_rules", {}).items():
            f.write(f"• {rule.upper().replace('_', ' ')}: {desc}\n")
        f.write("\n")

        f.write("4. STOCK BEHAVIORS\n")
        f.write("------------------\n")
        for stock, behavior in kb.get("stock_behaviors", {}).items():
            f.write(f"• {stock}: {behavior}\n")

        f.write("\n\n--- End of Master File ---")

    print(f"✅ Master knowledge file exported to: {output_path}")

if __name__ == "__main__":
    export_to_text()
