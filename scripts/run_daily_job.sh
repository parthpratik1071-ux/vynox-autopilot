#!/usr/bin/env bash
# Automated Daily Instagram Dispatch Runner
set -e

export PATH="/home/pratik/.local/bin:/home/pratik/.gemini/antigravity-ide/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
[ -f /home/pratik/.bashrc ] && source /home/pratik/.bashrc 2>/dev/null || true

PROJECT_DIR="/home/pratik/stickman-video-director"
cd "$PROJECT_DIR"
[ -f "$PROJECT_DIR/.env" ] && source "$PROJECT_DIR/.env"

echo "=========================================================="
echo "⏰ Running Daily Instagram Dispatcher at $(date)"
echo "=========================================================="

# Pull any remote updates first
git pull --rebase origin main || true

python3 scripts/daily_dispatcher.py

# Push archive and queue state to GitHub if changes occurred
git add projects/queue/ projects/archive/ projects/duplicate_registry.json projects/daily_dispatcher.log projects/auth_status.json || true
if ! git diff --cached --quiet; then
  git commit -m "chore: auto-sync local on-time dispatch state [skip ci]" || true
  git pull --rebase origin main || true
  git push origin main || true
fi

echo "🏁 Completed at $(date)"
