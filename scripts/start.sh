#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "==== LearnMate start ===="
echo "Backend : http://127.0.0.1:${BACKEND_PORT}"
echo "Frontend: http://127.0.0.1:${FRONTEND_PORT}"

if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
  echo "后端 venv 不存在：请先执行 ./scripts/setup.sh"
  exit 1
fi

# Start backend (FastAPI)
(
  cd "$BACKEND_DIR"
  source ".venv/bin/activate"
  uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT"
) &
BACK_PID="$!"
echo "Backend PID: $BACK_PID"

cleanup() {
  echo "Stopping..."
  kill "$BACK_PID" 2>/dev/null || true
  kill "$FRONT_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Start frontend (Vite dev; keeps /api proxy working)
(
  if [[ -d "$ROOT_DIR/.tooling/node/bin" ]]; then
    export PATH="$ROOT_DIR/.tooling/node/bin:$PATH"
  fi
  cd "$FRONTEND_DIR"
  if [[ ! -d "node_modules" ]]; then
    npm install
  fi
  npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT"
) &
FRONT_PID="$!"
echo "Frontend PID: $FRONT_PID"

wait -n "$BACK_PID" "$FRONT_PID"

