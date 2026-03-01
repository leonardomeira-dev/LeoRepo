#!/bin/bash
set -euo pipefail

# Only run in Claude Code remote (web) sessions
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo '{"async": true, "asyncTimeout": 300000}'

# Install npm dependencies
cd "$CLAUDE_PROJECT_DIR"
npm install

# Start Vite dev server in background so the preview tab works
nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/vite-dev.log 2>&1 &
echo "Vite dev server started on port 5173 (PID $!)"
