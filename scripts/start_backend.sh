#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR/backend"

if [[ ! -f ".venv/bin/activate" ]]; then
  echo "后端虚拟环境不存在: $ROOT_DIR/backend/.venv"
  exit 1
fi

source ".venv/bin/activate"

exec uvicorn main:app --host 0.0.0.0 --port 8000

