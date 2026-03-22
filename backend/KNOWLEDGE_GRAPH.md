# AI知识图谱模块文档

## 概述

AI知识图谱模块从学习资料文本中自动抽取知识实体和关系，构建可视化的知识图谱，帮助用户更好地理解和学习知识结构。

## 功能特性

1. ✅ **实体关系抽取** - 使用Gemini API从文本中抽取实体和关系
2. ✅ **三元组生成** - 生成标准的知识三元组 (entity1, relation, entity2)
3. ✅ **图结构构建** - 使用networkx构建知识图谱
4. ✅ **可视化展示** - 使用pyvis生成交互式知识图谱网页
5. ✅ **笔记关联** - 用户可以点击节点查看相关笔记

## 完整流程

```
文本
  ↓
使用 Gemini API 抽取实体关系
  ↓
生成三元组 (entity1, relation, entity2)
  ↓
构建 networkx 图结构
  ↓
使用 pyvis 生成可视化网页
```

## API端点

### 1. 从文本抽取实体关系

**端点**: `POST /api/knowledge-graph/extract`

**请求体**:
```json
{
  "text": "人工智能是计算机科学的分支。机器学习是AI的子领域。",
  "source_id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "实体和关系抽取成功",
  "triples_count": 2,
  "entities_count": 3,
  "relations_count": 2
}
```

### 2. 从文档抽取实体关系

**端点**: `POST /api/knowledge-graph/extract-from-document/{document_id}`

**说明**: 从已处理的文档中抽取实体和关系

### 3. 生成可视化

**端点**: `POST /api/knowledge-graph/visualize`

**查询参数**:
- `filename`: 输出文件名（可选）
- `height`: 画布高度（默认800px）
- `width`: 画布宽度（默认100%）

**响应**:
```json
{
  "success": true,
  "message": "知识图谱可视化生成成功",
  "file_path": "knowledge_graphs/kg_20231201_120000.html",
  "url": "/api/knowledge-graph/view/kg_20231201_120000.html",
  "statistics": {
    "nodes_count": 10,
    "edges_count": 15,
    "triples_count": 15
  }
}
```

### 4. 查看可视化

**端点**: `GET /api/knowledge-graph/view/{filename}`

**说明**: 返回生成的HTML可视化文件

### 5. 获取实体信息

**端点**: `GET /api/knowledge-graph/entity/{entity_name}`

**响应**:
```json
{
  "entity": "人工智能",
  "incoming_relations": [
    {
      "from": "计算机科学",
      "relation": "属于",
      "confidence": 0.9
    }
  ],
  "outgoing_relations": [
    {
      "to": "机器学习",
      "relation": "包含",
      "confidence": 0.85
    }
  ],
  "notes": [
    {
      "text": "相关文本片段...",
      "source_id": 1,
      "triple": ["人工智能", "包含", "机器学习"]
    }
  ],
  "degree": 5
}
```

### 6. 获取统计信息

**端点**: `GET /api/knowledge-graph/statistics`

**响应**:
```json
{
  "nodes_count": 20,
  "edges_count": 30,
  "triples_count": 30,
  "entities_count": 20,
  "relations_count": 8,
  "notes_count": 45
}
```

### 7. 获取三元组

**端点**: `GET /api/knowledge-graph/triples?format=json&limit=10`

**查询参数**:
- `format`: 格式（json或csv）
- `limit`: 限制数量（可选）

### 8. 从所有文档构建知识图谱

**端点**: `POST /api/knowledge-graph/build-from-documents`

**说明**: 批量处理所有已处理的文档

### 9. 清空知识图谱

**端点**: `DELETE /api/knowledge-graph/clear`

## 使用示例

### Python示例

```python
import requests

# 1. 从文本抽取实体关系
response = requests.post("http://localhost:8000/api/knowledge-graph/extract", json={
    "text": "人工智能是计算机科学的分支。机器学习是AI的子领域。",
    "source_id": 1
})
print(response.json())

# 2. 生成可视化
response = requests.post("http://localhost:8000/api/knowledge-graph/visualize")
result = response.json()
print(f"可视化文件: {result['url']}")

# 3. 获取实体信息
response = requests.get("http://localhost:8000/api/knowledge-graph/entity/人工智能")
print(response.json())

# 4. 获取统计信息
response = requests.get("http://localhost:8000/api/knowledge-graph/statistics")
print(response.json())
```

### JavaScript示例

```javascript
// 从文本抽取实体关系
const response = await fetch('http://localhost:8000/api/knowledge-graph/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: '人工智能是计算机科学的分支。机器学习是AI的子领域。',
    source_id: 1
  })
})

const result = await response.json()
console.log('抽取结果:', result)

// 生成可视化
const vizResponse = await fetch('http://localhost:8000/api/knowledge-graph/visualize', {
  method: 'POST'
})

const vizResult = await vizResponse.json()
console.log('可视化URL:', vizResult.url)
// 在新窗口打开可视化
window.open(vizResult.url, '_blank')
```

## 代码使用示例

### 直接使用KnowledgeGraph类

```python
from app.services.knowledge_graph import get_knowledge_graph

# 获取知识图谱实例
kg = get_knowledge_graph()

# 处理文本
text = """
人工智能（AI）是计算机科学的一个分支。
机器学习是AI的子领域。
深度学习是机器学习的子集。
"""

result = kg.process_text(text, source_id=1)
print(f"抽取了 {result['triples_count']} 个三元组")

# 生成可视化
kg.visualize("my_kg.html")

# 获取实体信息
info = kg.get_entity_info("人工智能")
print(f"实体信息: {info}")

# 获取统计信息
stats = kg.get_statistics()
print(f"节点数: {stats['nodes_count']}")
```

## 可视化特性

### 节点特性

- **大小**: 基于连接数（度）
- **颜色**: 统一蓝色主题
- **标签**: 显示实体名称
- **点击**: 可以查看相关笔记

### 边特性

- **方向**: 有向边，表示关系方向
- **标签**: 显示关系类型
- **宽度**: 基于置信度
- **颜色**: 基于关系类型

### 交互功能

- **拖拽**: 可以拖拽节点调整布局
- **缩放**: 鼠标滚轮缩放
- **点击**: 点击节点查看详细信息
- **悬停**: 悬停显示详细信息

## 实体关系抽取

### 使用Gemini API

系统使用Gemini API进行实体和关系抽取，提示词格式：

```
请从以下文本中抽取知识实体和它们之间的关系。

要求：
1. 识别文本中的主要实体（概念、人物、地点、事件等）
2. 识别实体之间的关系（如：属于、包含、导致、位于等）
3. 以三元组形式输出：(实体1, 关系, 实体2)
```

### 常见关系类型

- **属于/包含**: 层级关系
- **导致/影响**: 因果关系
- **位于/位于**: 空间关系
- **使用/基于**: 依赖关系
- **是/属于**: 分类关系

## 三元组格式

标准三元组格式：`(实体1, 关系, 实体2)`

示例：
- `(人工智能, 包含, 机器学习)`
- `(机器学习, 包含, 深度学习)`
- `(Python, 用于, AI开发)`

## 性能优化

### 1. 批量处理

使用 `build-from-documents` API批量处理所有文档：

```python
POST /api/knowledge-graph/build-from-documents
```

### 2. 增量更新

知识图谱支持增量添加，不会重复处理相同内容。

### 3. 可视化优化

- 使用物理引擎自动布局
- 支持大规模图谱（1000+节点）
- 异步生成HTML文件

## 注意事项

1. **Gemini API配置**: 需要配置 `GEMINI_API_KEY` 环境变量
2. **文本质量**: 输入文本质量影响抽取效果
3. **关系准确性**: 抽取的关系可能存在错误，需要人工审核
4. **存储**: 知识图谱数据存储在内存中，重启会丢失（可扩展持久化）

## 依赖安装

```bash
pip install networkx pyvis google-generativeai
```

## 相关文档

- [Gemini API配置](./GEMINI_SETUP.md)
- [知识库文档](./KNOWLEDGE_BASE.md)
- [RAG系统文档](./RAG_SYSTEM.md)






