# 项目中API使用情况

## 📍 使用API的地方

项目中主要使用 **Gemini API**，用于以下两个功能：

### 1. RAG问答系统
**位置**: 
- `backend/app/routers/chat.py` - 聊天路由
- `backend/app/services/gemini_service.py` - Gemini服务封装

**用途**: 
- 生成AI回答
- 流式响应生成

**调用位置**:
- `POST /api/chat/` - 标准问答
- `POST /api/chat/stream` - 流式问答

### 2. 知识图谱模块
**位置**: 
- `backend/app/services/knowledge_graph.py` - 知识图谱服务

**用途**: 
- 从文本中抽取实体和关系
- 生成知识三元组

**调用位置**:
- `POST /api/knowledge-graph/extract` - 从文本抽取
- `POST /api/knowledge-graph/extract-from-document/{id}` - 从文档抽取

## 🔄 替换为DeepSeek

DeepSeek API完全兼容OpenAI格式，可以轻松替换！






