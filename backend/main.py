"""
LearnMate Backend - FastAPI主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# 尽早加载 backend/.env，确保路由选择（Gemini/DeepSeek）能读到环境变量
try:
    from dotenv import load_dotenv  # type: ignore

    # 固定从本文件所在目录加载 .env，避免因为启动 cwd 不同而读不到配置
    load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
except Exception:
    # python-dotenv 未安装或加载失败不应影响服务启动
    pass

from app.routers import upload, document, search, chat, ocr, process, knowledge_graph, auth
from app.database import init_db
from app.utils.vector_store import vector_store
from app.services.knowledge_base import knowledge_base

app = FastAPI(
    title="LearnMate API",
    description="AI学习助手后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    # 开发环境常见访问方式：localhost / 127.0.0.1 / 0.0.0.0（以及不同端口）
    # 若你用局域网 IP 访问前端，也需要把对应来源加入这里。
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://1.0.0.127:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://0.0.0.0:3001",
        "http://1.0.0.127:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
        "http://1.0.0.127:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建上传文件目录
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)

# 挂载静态文件
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 注册路由
app.include_router(upload.router, prefix="/api/upload", tags=["文件上传"])
app.include_router(document.router, prefix="/api/document", tags=["文档管理"])
app.include_router(process.router, prefix="/api/process", tags=["文档处理"])
app.include_router(search.router, prefix="/api/search", tags=["语义搜索"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI问答"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR识别"])
app.include_router(knowledge_graph.router, prefix="/api/knowledge-graph", tags=["知识图谱"])
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()

    # 启动后自动从数据库重建内存向量索引（避免服务重启后“检索不到”）
    # 可通过环境变量关闭：
    # - AUTO_REBUILD_KB=false
    # 可选限制重建文档数（调试用）：
    # - AUTO_REBUILD_KB_LIMIT_DOCS=50
    auto_rebuild = os.getenv("AUTO_REBUILD_KB", "true").strip().lower() in {"1", "true", "yes", "y", "on"}
    if auto_rebuild:
        limit_docs_raw = os.getenv("AUTO_REBUILD_KB_LIMIT_DOCS", "").strip()
        limit_docs = int(limit_docs_raw) if limit_docs_raw.isdigit() else None
        try:
            rebuild_res = knowledge_base.rebuild_from_db(only_completed=True, limit_docs=limit_docs)
            print(
                "知识库自动重建结果:",
                {
                    "success": rebuild_res.get("success"),
                    "message": rebuild_res.get("message"),
                    "rebuilt_documents": rebuild_res.get("rebuilt_documents"),
                    "rebuilt_chunks": rebuild_res.get("rebuilt_chunks"),
                    "index_size": rebuild_res.get("index_size"),
                },
            )
        except Exception as e:
            print(f"知识库自动重建失败（不影响启动）：{e}")

    # 可选：启动时预热向量模型，避免第一次处理文档时卡很久
    # export PRELOAD_EMBEDDING_MODEL=true
    if os.getenv("PRELOAD_EMBEDDING_MODEL", "false").lower() == "true":
        try:
            vector_store._ensure_encoder()
        except Exception as e:
            print(f"向量模型预热失败（不影响启动）：{e}")


@app.get("/")
async def root():
    return {"message": "LearnMate API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

