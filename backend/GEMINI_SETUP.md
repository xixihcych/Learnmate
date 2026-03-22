# Gemini API配置指南

## 获取API密钥

### 步骤1: 访问Google AI Studio

1. 打开浏览器，访问：https://makersuite.google.com/app/apikey
2. 使用Google账号登录

### 步骤2: 创建API密钥

1. 点击 "Create API Key" 按钮
2. 选择或创建Google Cloud项目
3. 复制生成的API密钥

### 步骤3: 配置环境变量

#### 方法1: 使用.env文件（推荐）

1. 在项目根目录创建 `.env` 文件：

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_NAME=gemini-pro
```

2. 确保 `.env` 文件已添加到 `.gitignore`（不要提交API密钥到Git）

#### 方法2: 设置系统环境变量

**Windows (PowerShell)**:
```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

**Windows (CMD)**:
```cmd
set GEMINI_API_KEY=your_api_key_here
```

**Linux/macOS**:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

**永久设置（Linux/macOS）**:
```bash
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 验证配置

运行测试脚本：

```bash
python test_rag.py
```

如果配置正确，应该能看到Gemini服务初始化成功的消息。

## 可用模型

- `gemini-pro`: 标准模型（推荐）
- `gemini-pro-vision`: 支持图像输入
- `gemini-ultra`: 更强大的模型（可能需要特殊权限）

## 注意事项

1. **API配额**: 免费层有使用限制，注意配额使用情况
2. **安全性**: 不要将API密钥提交到Git仓库
3. **费用**: 查看Google AI的定价信息
4. **区域限制**: 某些地区可能无法使用Gemini API

## 故障排除

### 错误: API密钥未设置

```
ValueError: Gemini API密钥未设置
```

**解决**: 检查环境变量是否正确设置

### 错误: API密钥无效

```
Exception: Gemini API调用失败: API key not valid
```

**解决**: 
1. 检查API密钥是否正确
2. 确认API密钥未被撤销
3. 检查API是否已启用

### 错误: 配额超限

```
Exception: Quota exceeded
```

**解决**: 
1. 等待配额重置
2. 升级到付费计划
3. 减少API调用频率

## 相关链接

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API文档](https://ai.google.dev/docs)
- [API密钥管理](https://console.cloud.google.com/apis/credentials)






