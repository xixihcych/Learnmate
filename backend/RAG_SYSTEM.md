# RAG问答系统文档

## 概述

RAG（Retrieval-Augmented Generation）问答系统结合了向量搜索和LLM生成能力，实现基于知识库的智能问答。

## 完整流程

1. **用户输入问题** - 接收用户的问题
2. **在FAISS中检索相关文本** - 使用向量相似度搜索找到最相关的文档片段
3. **将文本作为上下文** - 将检索到的文本整理成上下文
4. **调用 Gemini API 生成回答** - 基于上下文和问题生成回答

## 架构组件

### 1. 知识库检索 (`app/services/knowledge_base.py`)

负责从FAISS向量数据库中检索相关文本：

```python
from app.services.knowledge_base import knowledge_base

# 检索相关文本
results = knowledge_base.search(
    query="用户问题",
    top_k=5
)
```

### 2. Gemini服务 (`app/services/gemini_service.py`)

负责调用Gemini API生成回答：

```python
from app.services.gemini_service import get_gemini_service

gemini_service = get_gemini_service()
response = gemini_service.generate_response(
    query="用户问题",
    context=["上下文1", "上下文2"]
)
```

### 3. RAG问答路由 (`app/routers/chat.py`)

整合检索和生成流程：

```python
POST /api/chat/
```

## API端点

### 1. 标准问答接口

**端点**: `POST /api/chat/`

**请求体**:
```json
{
  "message": "什么是人工智能？",
  "session_id": "optional-session-id",
  "document_ids": [1, 2, 3]  // 可选：限制搜索范围
}
```

**响应**:
```json
{
  "response": "AI生成的回答...",
  "session_id": "session-id",
  "sources": [
    {
      "document_id": 1,
      "filename": "document.pdf",
      "chunk_text": "相关文本片段...",
      "score": 0.1234
    }
  ]
}
```

### 2. 流式问答接口

**端点**: `POST /api/chat/stream`

**特点**:
- 实时返回生成的内容
- 使用Server-Sent Events (SSE)
- 适合前端实时显示

**响应格式**:
```
data: {"chunk": "生成的文本片段", "done": false}

data: {"chunk": "", "done": true, "full_response": "完整回答"}
```

## 配置

### 1. 环境变量配置

创建 `.env` 文件：

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-pro  # 可选
```

### 2. 获取Gemini API密钥

1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账号
3. 创建API密钥
4. 将密钥添加到 `.env` 文件

## 使用示例

### Python示例

```python
import requests

# 发送问题
response = requests.post("http://localhost:8000/api/chat/", json={
    "message": "什么是机器学习？",
    "document_ids": [1, 2]  # 可选
})

result = response.json()
print(f"回答: {result['response']}")
print(f"来源: {[s['filename'] for s in result['sources']]}")
```

### JavaScript示例

```javascript
// 标准问答
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '什么是机器学习？',
    document_ids: [1, 2]  // 可选
  })
})

const result = await response.json()
console.log('回答:', result.response)
console.log('来源:', result.sources.map(s => s.filename))

// 流式问答
const streamResponse = await fetch('http://localhost:8000/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '什么是机器学习？'
  })
})

const reader = streamResponse.body.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  
  const chunk = decoder.decode(value)
  const lines = chunk.split('\n')
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6))
      if (data.chunk) {
        console.log(data.chunk)  // 实时显示
      }
      if (data.done) {
        console.log('完整回答:', data.full_response)
      }
    }
  }
}
```

## 工作流程详解

### 步骤1: 用户输入问题

用户通过API发送问题：
```json
{
  "message": "什么是人工智能？"
}
```

### 步骤2: FAISS检索相关文本

系统在知识库中搜索最相关的文本块：

```python
# 在knowledge_base.search()中执行
results = knowledge_base.search(
    query="什么是人工智能？",
    top_k=5  # 返回前5个最相关的结果
)
```

**检索过程**：
1. 将问题转换为向量（embedding）
2. 在FAISS索引中搜索最相似的向量
3. 返回对应的文本块和相似度分数

### 步骤3: 构建上下文

将检索到的文本整理成上下文：

```python
context_texts = [
    "人工智能是计算机科学的一个分支...",
    "机器学习是AI的一个子领域...",
    # ...更多相关文本
]
```

### 步骤4: 调用Gemini API生成回答

将问题和上下文发送给Gemini：

```python
prompt = f"""
你是一个智能助手，基于提供的上下文信息回答用户的问题。

上下文信息：
[来源1]
人工智能是计算机科学的一个分支...

[来源2]
机器学习是AI的一个子领域...

用户问题：什么是人工智能？

请基于上述上下文信息回答用户的问题：
"""

response = gemini_model.generate_content(prompt)
```

## 提示词工程

### 默认系统提示词

```
你是一个智能助手，基于提供的上下文信息回答用户的问题。
请遵循以下规则：
1. 只基于提供的上下文信息回答问题
2. 如果上下文中没有相关信息，请明确说明
3. 回答要准确、简洁、有帮助
4. 如果上下文信息有多个来源，请综合这些信息
5. 使用中文回答
```

### 自定义提示词

可以在调用时自定义：

```python
gemini_service.generate_response(
    query="问题",
    context=["上下文"],
    system_prompt="你的自定义提示词..."
)
```

## 性能优化

### 1. 检索优化

- **top_k值**: 5-10个结果通常足够
- **相似度阈值**: 过滤低质量结果
- **文档过滤**: 限制搜索范围提高速度

### 2. 生成优化

- **temperature**: 0.7（平衡创造性和准确性）
- **max_tokens**: 限制生成长度
- **上下文长度**: 控制上下文文本数量

### 3. 缓存策略

- 缓存常见问题的回答
- 缓存检索结果
- 使用会话历史

## 错误处理

### 常见错误

1. **API密钥错误**
   ```
   Gemini API配置错误：API密钥未设置
   ```
   解决：检查 `GEMINI_API_KEY` 环境变量

2. **检索结果为空**
   ```
   抱歉，我在知识库中没有找到相关信息
   ```
   解决：上传相关文档到知识库

3. **API调用失败**
   - 网络问题
   - API配额限制
   - 模型不可用

### 降级策略

如果Gemini API调用失败，系统会：
1. 返回基于检索结果的简化回答
2. 显示检索到的相关文本
3. 提示用户稍后重试

## 最佳实践

1. **知识库质量**
   - 上传高质量、相关的文档
   - 定期更新知识库
   - 清理过时信息

2. **问题优化**
   - 使用清晰、具体的问题
   - 避免过于宽泛的问题
   - 提供必要的上下文

3. **回答质量**
   - 检查来源的可靠性
   - 验证回答的准确性
   - 提供来源引用

4. **用户体验**
   - 使用流式响应提升体验
   - 显示检索来源
   - 提供反馈机制

## 依赖安装

```bash
pip install google-generativeai python-dotenv
```

## 相关文档

- [Gemini API文档](https://ai.google.dev/docs)
- [RAG最佳实践](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [向量搜索文档](./KNOWLEDGE_BASE.md)






