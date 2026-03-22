#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v systemctl >/dev/null 2>&1; then
  echo "未找到 systemctl（systemd），无法安装自启动服务。"
  exit 1
fi

USER_NAME="${SUDO_USER:-$USER}"
SERVICE_DIR="/etc/systemd/system"

echo "将安装 LearnMate systemd 服务到: $SERVICE_DIR"
echo "使用用户: $USER_NAME"

# 生成服务文件到临时目录
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cat >"$TMP_DIR/learnmate-backend.service" <<EOF
[Unit]
Description=LearnMate Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$ROOT_DIR/backend
Environment=PYTHONUNBUFFERED=1
ExecStart=$ROOT_DIR/scripts/start_backend.sh
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

cat >"$TMP_DIR/learnmate-frontend.service" <<EOF
[Unit]
Description=LearnMate Frontend (Vite preview)
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$ROOT_DIR/frontend
Environment=NODE_ENV=production
ExecStart=$ROOT_DIR/scripts/start_frontend.sh
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

sudo mkdir -p "$SERVICE_DIR"
sudo cp "$TMP_DIR/learnmate-backend.service" "$SERVICE_DIR/learnmate-backend.service"
sudo cp "$TMP_DIR/learnmate-frontend.service" "$SERVICE_DIR/learnmate-frontend.service"

sudo systemctl daemon-reload
sudo systemctl enable --now learnmate-backend.service
sudo systemctl enable --now learnmate-frontend.service

echo "安装完成。常用命令："
echo "  sudo systemctl status learnmate-backend learnmate-frontend"
echo "  sudo journalctl -u learnmate-backend -f"
echo "  sudo journalctl -u learnmate-frontend -f"

