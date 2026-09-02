#!/bin/bash
# ORACLE CLI Runner
# For Windows/Powershell users, run this via bash or WSL, or use the demo.py directly

echo "=========================================================="
echo "    ORACLE — Omniscient Reasoning & Capital Allocation    "
echo "=========================================================="
echo ""
echo "Starting ORACLE in live scan mode..."

# Load virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/Scripts/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ensure PYTHONPATH is set so python can find the oracle module
export PYTHONPATH=$(pwd)

# Start the main loop
python oracle/main.py
