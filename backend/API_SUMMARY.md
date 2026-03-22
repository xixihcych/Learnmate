# API使用情况总结

## 📍 项目中使用API的地方

### 1. RAG问答系统 ✅
**位置**: 
- `backend/app/routers/chat.py`
- `backend/app/services/gemini_service.py` 或 `deepseek_service.py`

**功能**: 
- 生成AI回答
- 流式响应

**API端点**:
- `POST /api/chat/` - 标准问答
- `POST /api/chat/stream` - 流式问答

### 2. 知识图谱模块 ✅
**位置**: 
- `backend/app/services/knowledge_graph.py`

**功能**: 
- 从文本抽取实体和关系
- 生成知识三元组

**API端点**:
- `POST /api/knowledge-graph/extract` - 从文本抽取
- `POST /api/knowledge-graph/extract-from-document/{id}` - 从文档抽取

## 🔄 支持的LLM服务

项目现在支持**两种LLM服务**，可以通过环境变量切换：

### 选项1: Gemini API（默认）
```env
USE_DEEPSEEK=false
GEMINI_API_KEY=your_gemini_api_key
```

### 选项2: DeepSeek API（推荐国内使用）
```env
USE_DEEPSEEK=true
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## ✅ DeepSeek完全支持！

**是的，可以用DeepSeek！** 项目已经支持DeepSeek API。

### DeepSeek优势
- ✅ 国内访问速度快
- ✅ 价格更优惠
- ✅ 中文支持好
- ✅ 兼容OpenAI格式
- ✅ 代码已集成，只需配置环境变量

### 配置方法

1. **获取DeepSeek API密钥**
   - 访问：https://platform.deepseek.com/
   - 注册并创建API密钥

2. **配置环境变量**
   在 `backend/.env` 文件中：
   ```env
   USE_DEEPSEEK=true
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

3. **安装依赖**（已包含）
   ```bash
   pip install openai
   ```

4. **重启服务**
   重启后端服务即可使用DeepSeek！

## 📝 其他API使用

### 内部API（无需配置）
- **FAISS向量搜索** - 本地运行，无需API
- **PaddleOCR** - 本地运行，首次下载模型
- **sentence-transformers** - 本地运行，首次下载模型

### 可选API
- **Tesseract OCR** - 可选，需要本地安装（不是API调用）

## 🎯 总结

**使用API的地方只有2个**：
1. ✅ RAG问答 → 已支持DeepSeek
2. ✅ 知识图谱 → 已支持DeepSeek

**其他都是本地处理**，无需外部API！






