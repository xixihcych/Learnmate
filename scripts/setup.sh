#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

echo "==== LearnMate setup ===="

# Python
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "未找到 python: $PYTHON_BIN"
  exit 1
fi

mkdir -p "$BACKEND_DIR"
cd "$BACKEND_DIR"

echo "[1/4] Backend: create venv (backend/.venv) if needed"
if [[ ! -d ".venv" ]]; then
  "$PYTHON_BIN" -m venv .venv
fi

source ".venv/bin/activate"

echo "[2/4] Backend: install python deps"
python -m pip install --upgrade pip
pip install -r requirements.txt

# Embeddings are required for KB / RAG retrieval.
INSTALL_EMBEDDINGS="${INSTALL_EMBEDDINGS:-true}"
if [[ "$INSTALL_EMBEDDINGS" == "true" ]]; then
  echo "[2/4] Install sentence-transformers (embedding model runtime)"
  # NOTE: this may trigger large downloads (PyTorch/weights) depending on your environment.
  pip install -U sentence-transformers
fi

# OCR is optional. If user enables ENABLE_OCR=true, they likely want OCR libs too.
OCR_ENABLE="${OCR_ENABLE:-false}"
if [[ -f "$BACKEND_DIR/.env" ]]; then
  # Read ENABLE_OCR from backend/.env if present (best effort).
  OCR_ENABLE="$(grep -E '^ENABLE_OCR=' "$BACKEND_DIR/.env" | tail -n 1 | cut -d= -f2 | tr -d '\r' || true)"
  OCR_ENABLE="${OCR_ENABLE:-false}"
fi

if [[ "${OCR_ENABLE,,}" == "true" ]]; then
  echo "[2/4] Install OCR deps: easyocr"
  pip install -U easyocr
fi

echo "[3/4] Frontend: install node deps"
cd "$FRONTEND_DIR"

# 若本机没有 Node，可把便携 Node 放在项目根目录 .tooling/node/bin（可选）；否则使用系统 PATH 中的 node/npm
if [[ -d "$ROOT_DIR/.tooling/node/bin" ]]; then
  export PATH="$ROOT_DIR/.tooling/node/bin:$PATH"
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "未找到 npm，请先安装 Node.js 18+（https://nodejs.org/）"
  exit 1
fi
if [[ ! -d "node_modules" ]]; then
  npm install
fi

echo "[4/4] Setup complete"
echo "Next: run ./scripts/start.sh"

