# 环境配置指南

## 环境选择

项目**不需要conda**，可以使用Python自带的venv虚拟环境。但如果您习惯使用conda，也可以使用。

## 方式1: 使用venv（推荐，简单）

### Windows

```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Linux/macOS

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 方式2: 使用conda（可选）

如果您已经安装了conda，也可以使用：

### 创建conda环境

```bash
cd backend

# 创建conda环境（Python 3.8+）
conda create -n learnmate python=3.10

# 激活环境
conda activate learnmate

# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 推荐使用venv的原因

1. ✅ **Python自带** - 无需额外安装
2. ✅ **轻量级** - 比conda更小更快
3. ✅ **简单** - 命令更简单
4. ✅ **足够用** - 对于这个项目完全够用

## conda的优势（如果选择使用）

1. ✅ **包管理更好** - 处理复杂依赖关系
2. ✅ **科学计算** - 如果项目需要numpy、pandas等科学计算库
3. ✅ **多Python版本** - 方便切换Python版本

## 当前项目依赖

项目主要依赖：
- FastAPI、uvicorn（Web框架）
- sentence-transformers、faiss（AI库）
- pdfplumber、python-docx（文档解析）
- openai（DeepSeek API）
- networkx、pyvis（知识图谱）

**这些都可以用pip安装，不需要conda的特殊功能。**

## 建议

**推荐使用venv**，因为：
- 项目依赖不复杂
- venv足够用
- 更简单直接

**只有在以下情况才考虑conda**：
- 您已经习惯使用conda
- 需要管理多个Python版本
- 需要科学计算环境

## 验证环境

无论使用哪种方式，激活环境后验证：

```bash
# 检查Python版本（需要3.8+）
python --version

# 检查pip
pip --version

# 安装依赖
pip install -r requirements.txt

# 测试导入
python -c "import fastapi; print('FastAPI OK')"
python -c "import openai; print('OpenAI OK')"
```

## 总结

- ❌ **不需要conda** - venv完全够用
- ✅ **推荐venv** - 简单直接
- ✅ **conda可选** - 如果习惯使用也可以






