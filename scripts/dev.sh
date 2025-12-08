#!/usr/bin/env bash
set -euo pipefail

# scripts/dev.sh
# Start a simple static server, open the default browser, and restart on file changes (if fswatch is available)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-${PORT:-8000}}"

cd "$REPO_ROOT"

start_server() {
  # start server in background
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  SERVER_PID=$!
  echo "Started server (PID $SERVER_PID) on http://localhost:$PORT"
}

echo "Starting dev server in $REPO_ROOT"
start_server

# Open browser (macOS: open, Linux: xdg-open)
if command -v open >/dev/null 2>&1; then
  open "http://localhost:$PORT"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:$PORT"
else
  echo "Open http://localhost:$PORT in your browser";
fi

# If fswatch is available, use it to restart the server on changes
if command -v fswatch >/dev/null 2>&1; then
  echo "Watching for file changes with fswatch..."
  fswatch -0 . | while read -r -d '' event; do
    echo "Change detected ($event) — restarting server..."
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    start_server
  done
else
  echo "No file watcher found (fswatch). Server will run without auto-restart."
  echo "Install fswatch (brew install fswatch) for automatic reload on changes."
  wait "$SERVER_PID"
fi
