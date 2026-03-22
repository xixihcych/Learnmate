# LearnMate Backend

LearnMate后端服务，基于FastAPI构建。

## 功能特性

- 📄 文件上传（PDF/Word/PPT）
- 🔍 文档解析和文本提取
- 👁️ OCR识别（图片文字提取）
- 🔎 语义搜索（基于FAISS向量数据库）
- 💬 AI问答（RAG检索增强生成）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 http://localhost:8000 启动

## API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境要求

- Python 3.8+
- Tesseract OCR（用于OCR功能，需要单独安装）

### Windows安装Tesseract OCR

1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后，将安装路径添加到系统PATH环境变量
3. 或设置环境变量：`TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata`

## 注意事项

1. OCR功能需要安装Tesseract OCR引擎
2. 首次运行会自动创建SQLite数据库
3. 向量数据库使用FAISS，首次使用会下载sentence-transformers模型
4. AI问答功能目前是简化版本，实际应用中需要集成真实的LLM API（如OpenAI、Claude等）






