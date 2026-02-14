#!/bin/bash

# --- ANZA PRO ONE-CLICK LAUNCHER (LINUX) ---

if command -v python3 &>/dev/null; then
    PY=python3
elif command -v python &>/dev/null; then
    PY=python
else
    echo "❌ ERROR: Python not found."
    exit 1
fi

$PY launcher.py --auto
