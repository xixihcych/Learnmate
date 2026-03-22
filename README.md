# LearnMate（GitHub 精简版）

本目录为可上传 GitHub 的**源码快照**：不含虚拟环境、`node_modules`、上传文件、本地数据库及**模型权重**。

## 目录结构

- `backend/` — FastAPI 后端
- `frontend/` — Vite + React 前端
- `scripts/` — 一键安装与启动
- `models/` — 放置向量模型（见 `models/README.md`，勿提交大文件）

## 环境要求

- Python 3.10+（建议 3.11）
- Node.js 18+ 与 npm（或使用项目根目录可选的 `.tooling/node` 便携 Node）

## 快速开始

```bash
cd learnmate-github

# 1. 后端环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入 API Key；按需设置 EMBEDDING_MODEL_PATH、EMBEDDING_DEVICE 等

# 2. 创建运行时目录（若不存在）
mkdir -p backend/uploads backend/processed backend/knowledge_graphs

# 3. 安装依赖（创建 backend/.venv、安装前端 npm 包）
chmod +x scripts/*.sh
./scripts/setup.sh

# 4. 启动（后端 8000 + 前端开发服 3000，日志在 /tmp）
./scripts/start.sh
```

- 前端开发地址：<http://localhost:3000>
- 后端 API 文档：<http://localhost:8000/docs>

## 生产/常驻（可选）

- `scripts/start_backend.sh` — 仅后端（需已存在 `backend/.venv`）
- `scripts/start_frontend.sh` — 构建并以 `preview` 提供静态前端（端口 3000）
- `scripts/install_systemd.sh` — systemd 用户服务示例

## 说明

- **向量模型**需自行下载或运行 `scripts/download_embedding_model.sh`（若存在），详见 `models/README.md`。
- 不要将真实 `.env`、`*.db`、`uploads/`、`models/` 下的大文件推送到公开仓库。

