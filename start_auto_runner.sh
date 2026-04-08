#!/bin/bash
# Launches auto_runner.py in the background with the correct Python environment
# Usage: bash start_auto_runner.sh

cd "$(dirname "$0")"

PYTHON=/Library/Frameworks/Python.framework/Versions/3.12/bin/python3.12

nohup $PYTHON auto_runner.py >> data/auto_runner.log 2>&1 &
echo $! > data/auto_runner.pid

echo "✅ Auto runner started (PID: $(cat data/auto_runner.pid))"
echo "   Checking inbox every 10 minutes."
echo ""
echo "   To see activity:  tail -f data/auto_runner.log"
echo "   To stop:          bash stop_auto_runner.sh"
