# 知识库向量搜索系统文档

## 概述

知识库向量搜索系统使用FAISS实现高效的语义搜索功能。系统完整实现了以下流程：

1. **文本切分** - 将长文本分割成适合向量化的块
2. **生成embedding** - 使用sentence-transformers生成文本向量
3. **存入FAISS** - 将向量存储到FAISS索引中
4. **用户搜索** - 返回最相似的文本块

## 架构设计

### 核心组件

1. **KnowledgeBase** (`app/services/knowledge_base.py`)
   - 知识库管理类
   - 整合文本切分、embedding生成、FAISS存储和搜索

2. **VectorStore** (`app/utils/vector_store.py`)
   - FAISS向量存储封装
   - 使用sentence-transformers生成embeddings

3. **TextSplitter** (`app/utils/text_splitter.py`)
   - 文本切分工具
   - 支持多种切分策略

## 工作流程

### 1. 添加文档到知识库

```python
from app.services.knowledge_base import knowledge_base

# 添加文档
chunk_count = knowledge_base.add_document(
    document_id=1,
    text="文档内容...",
    filename="document.pdf",
    metadata={'category': 'AI'}
)

print(f"生成了 {chunk_count} 个文本块")
```

**流程说明**：
1. 文本切分：将文档文本分割成多个文本块
2. 生成embedding：为每个文本块生成向量表示
3. 存入FAISS：将向量添加到FAISS索引
4. 保存元数据：保存文本块和元数据到数据库

### 2. 搜索知识库

```python
# 搜索
results = knowledge_base.search(
    query="人工智能",
    top_k=5,
    document_ids=[1, 2, 3]  # 可选：限制搜索范围
)

for result in results:
    print(f"文档: {result['filename']}")
    print(f"相似度: {result['similarity']:.2%}")
    print(f"文本: {result['chunk_text']}")
```

**流程说明**：
1. 生成查询embedding：将查询文本转换为向量
2. FAISS搜索：在索引中查找最相似的向量
3. 返回结果：按相似度排序返回最相似的文本块

## API端点

### 1. 语义搜索

**端点**: `POST /api/search/`

**请求体**:
```json
{
  "query": "搜索查询文本",
  "top_k": 5,
  "document_ids": [1, 2, 3]  // 可选
}
```

**响应**:
```json
[
  {
    "document_id": 1,
    "filename": "document.pdf",
    "chunk_text": "匹配的文本块内容...",
    "score": 0.1234,
    "page_number": 1
  }
]
```

### 2. 知识库统计

**端点**: `GET /api/search/stats`

**响应**:
```json
{
  "total_chunks": 150,
  "total_documents": 10,
  "index_dimension": 384,
  "index_size": 150
}
```

### 3. 文档统计

**端点**: `GET /api/search/document/{document_id}/stats`

**响应**:
```json
{
  "document_id": 1,
  "chunk_count": 15,
  "avg_chunk_size": 450
}
```

## 文本切分策略

### 1. 固定大小切分

```python
from app.utils.text_splitter import split_text

chunks = split_text(
    text="长文本...",
    chunk_size=500,      # 每个块500字符
    chunk_overlap=50    # 重叠50字符
)
```

### 2. 按段落切分

```python
from app.utils.text_splitter import split_text_by_paragraph

chunks = split_text_by_paragraph(
    text="段落1\n\n段落2\n\n段落3",
    max_chunk_size=1000
)
```

### 3. 智能切分

```python
from app.utils.text_splitter import smart_split_text

chunks = smart_split_text(
    text="长文本...",
    chunk_size=500,
    chunk_overlap=50
)
```

**特点**：
- 优先在段落边界分割
- 段落太长时在句子边界分割
- 保持语义完整性

## 配置参数

### KnowledgeBase参数

- `chunk_size`: 文本块大小（默认500字符）
- `chunk_overlap`: 文本块重叠大小（默认50字符）

### VectorStore参数

- `model_name`: embedding模型名称（默认'paraphrase-multilingual-MiniLM-L12-v2'）
  - 支持中英文
  - 向量维度：384

## 使用示例

### Python代码示例

```python
from app.services.knowledge_base import knowledge_base

# 1. 添加文档
chunk_count = knowledge_base.add_document(
    document_id=1,
    text="文档内容...",
    filename="doc.pdf"
)

# 2. 搜索
results = knowledge_base.search("查询文本", top_k=5)

# 3. 获取统计信息
stats = knowledge_base.get_stats()
print(f"总文本块数: {stats['total_chunks']}")
```

### API调用示例

```python
import requests

# 搜索
response = requests.post("http://localhost:8000/api/search/", json={
    "query": "人工智能",
    "top_k": 5
})

results = response.json()
for result in results:
    print(f"{result['filename']}: {result['chunk_text']}")
```

### JavaScript示例

```javascript
// 搜索
const response = await fetch('http://localhost:8000/api/search/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '人工智能',
    top_k: 5
  })
})

const results = await response.json()
results.forEach(result => {
  console.log(`${result.filename}: ${result.chunk_text}`)
})
```

## 性能优化

### 1. 文本块大小

- **太小**：可能丢失上下文，embedding质量下降
- **太大**：搜索精度下降，内存占用增加
- **推荐**：300-800字符，根据文档类型调整

### 2. 重叠大小

- **作用**：保持上下文连续性
- **推荐**：chunk_size的10-20%

### 3. FAISS索引类型

当前使用 `IndexFlatL2`（精确搜索）：
- 优点：搜索精度高
- 缺点：搜索速度随数据量线性增长

**大规模数据建议**：
- 使用 `IndexIVFFlat`（近似搜索）
- 使用 `IndexHNSW`（图索引，速度快）

## 持久化

### 保存索引

```python
knowledge_base.save_index("knowledge_base.index")
```

### 加载索引

```python
knowledge_base.load_index("knowledge_base.index")
```

**注意**：
- 索引文件：`.index`（FAISS索引）
- 元数据文件：`.meta`（pickle格式）

## 最佳实践

1. **文本预处理**
   - 清理多余空白
   - 统一编码格式
   - 移除特殊字符（可选）

2. **切分策略选择**
   - 技术文档：按段落切分
   - 对话记录：按句子切分
   - 长文章：智能切分

3. **搜索优化**
   - 使用合适的top_k值（5-10）
   - 根据需求过滤文档ID
   - 设置最小相似度阈值

4. **索引管理**
   - 定期保存索引
   - 备份元数据
   - 监控索引大小

## 常见问题

### Q: 如何提高搜索准确率？

A: 
1. 调整文本块大小
2. 使用更好的embedding模型
3. 增加文本块重叠
4. 使用reranking（二次排序）

### Q: 搜索速度慢怎么办？

A:
1. 使用GPU加速embedding生成
2. 使用FAISS的近似搜索索引
3. 限制搜索的文档范围
4. 减少top_k值

### Q: 如何处理新文档？

A:
1. 解析文档提取文本
2. 调用 `add_document()` 添加到知识库
3. 可选：保存索引

### Q: 如何删除文档？

A:
```python
knowledge_base.delete_document(document_id)
```

注意：FAISS不支持直接删除，需要重建索引或使用ID映射。

## 依赖安装

```bash
pip install faiss-cpu sentence-transformers numpy
```

## 相关文档

- [FAISS文档](https://github.com/facebookresearch/faiss)
- [sentence-transformers文档](https://www.sbert.net/)
- [向量搜索最佳实践](https://www.pinecone.io/learn/vector-search-best-practices/)






