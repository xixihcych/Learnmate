#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

NODE_DIR="$ROOT_DIR/.tooling/node/bin"
if [[ -d "$NODE_DIR" ]]; then
  export PATH="$NODE_DIR:$PATH"
fi

cd "$ROOT_DIR/frontend"

if [[ ! -d "node_modules" ]]; then
  npm install
fi

npm run build

# 用 preview 提供静态站点（适合常驻服务，比 dev 更稳定）
exec npm run preview -- --host 0.0.0.0 --port 3000

