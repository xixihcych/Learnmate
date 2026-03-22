# DeepSeek API配置指南

## 概述

项目现在支持使用 **DeepSeek API** 替代 Gemini API！

DeepSeek API完全兼容OpenAI格式，可以用于：
1. **RAG问答系统** - 生成AI回答
2. **知识图谱模块** - 抽取实体和关系

## 配置步骤

### 1. 获取DeepSeek API密钥

1. 访问：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入API Keys页面
4. 创建新的API密钥
5. 复制密钥

### 2. 配置环境变量

在 `backend/` 目录的 `.env` 文件中添加：

```env
# 使用DeepSeek（设置为true）
USE_DEEPSEEK=true

# DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

**或者**继续使用Gemini：

```env
# 使用Gemini（默认，不设置或设置为false）
USE_DEEPSEEK=false

# Gemini API密钥
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 安装依赖

DeepSeek使用OpenAI兼容的SDK：

```bash
pip install openai
```

（已在requirements.txt中包含）

## 使用方法

### 切换LLM服务

通过环境变量 `USE_DEEPSEEK` 控制：

- `USE_DEEPSEEK=true` → 使用DeepSeek API
- `USE_DEEPSEEK=false` 或不设置 → 使用Gemini API（默认）

### 代码示例

```python
# 自动根据环境变量选择服务
from app.services.deepseek_service import get_deepseek_service
# 或
from app.services.gemini_service import get_gemini_service

# 使用方式完全相同
service = get_deepseek_service()
response = service.generate_response(
    query="问题",
    context=["上下文1", "上下文2"]
)
```

## DeepSeek模型

默认使用 `deepseek-chat` 模型，也可以使用其他模型：

- `deepseek-chat` - 标准对话模型（推荐）
- `deepseek-coder` - 代码专用模型

在代码中可以指定：

```python
service.generate_response(
    query="问题",
    context=context,
    model="deepseek-chat"  # 或 "deepseek-coder"
)
```

## API端点

所有API端点保持不变，只需配置环境变量即可切换：

- `POST /api/chat/` - RAG问答（自动使用配置的LLM）
- `POST /api/knowledge-graph/extract` - 知识图谱抽取（自动使用配置的LLM）

## 优势对比

### DeepSeek优势
- ✅ 国内访问速度快
- ✅ 价格更优惠
- ✅ 中文支持好
- ✅ 兼容OpenAI格式

### Gemini优势
- ✅ Google官方支持
- ✅ 多模态支持（图像等）
- ✅ 免费额度较高

## 故障排除

### 错误: API密钥未设置

```
ValueError: DeepSeek API密钥未设置
```

**解决**: 检查 `DEEPSEEK_API_KEY` 环境变量

### 错误: 无法导入openai

```
ImportError: openai库未安装
```

**解决**: 
```bash
pip install openai
```

### 错误: API调用失败

检查：
1. API密钥是否正确
2. 网络连接是否正常
3. API配额是否充足

## 相关文档

- [DeepSeek API文档](https://platform.deepseek.com/api_docs)
- [OpenAI兼容性说明](https://platform.deepseek.com/api_docs#compatibility)






