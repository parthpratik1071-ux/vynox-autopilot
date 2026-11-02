#!/usr/bin/env bash
# Automated Daily Instagram Dispatch Runner
set -e

export PATH="/home/pratik/.local/bin:/home/pratik/.gemini/antigravity-ide/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
[ -f /home/pratik/.bashrc ] && source /home/pratik/.bashrc 2>/dev/null || true

PROJECT_DIR="/home/pratik/stickman-video-director"
cd "$PROJECT_DIR"

echo "=========================================================="
echo "⏰ Running Daily Instagram Dispatcher at $(date)"
echo "=========================================================="

python3 scripts/daily_dispatcher.py

echo "🏁 Completed at $(date)"
