# 文件上传API文档

## 概述

文件上传API支持上传PDF、PPT、Word文档和图片文件，文件会自动保存到 `uploads` 文件夹，并返回文件路径。

## API端点

### 1. 单文件上传

**端点**: `POST /api/upload/`

**请求格式**: `multipart/form-data`

**参数**:
- `file` (required): 要上传的文件

**支持的文件类型**:
- 文档: `.pdf`, `.doc`, `.docx`, `.ppt`, `.pptx`
- 图片: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.tif`

**文件大小限制**: 最大 50MB

**响应示例**:
```json
{
  "success": true,
  "message": "文件上传成功",
  "filename": "example.pdf",
  "file_path": "uploads/20231201_143022_a1b2c3d4_example.pdf",
  "file_size": 1024000,
  "file_type": "pdf"
}
```

**错误响应**:
```json
{
  "detail": "不支持的文件类型: .txt。支持的类型: .pdf, .doc, .docx, .ppt, .pptx, .jpg, .jpeg, .png, .gif, .bmp, .webp, .tiff, .tif"
}
```

### 2. 批量文件上传

**端点**: `POST /api/upload/multiple`

**请求格式**: `multipart/form-data`

**参数**:
- `files` (required): 要上传的文件列表（多个文件）

**响应示例**:
```json
[
  {
    "success": true,
    "message": "文件上传成功",
    "filename": "file1.pdf",
    "file_path": "uploads/20231201_143022_a1b2c3d4_file1.pdf",
    "file_size": 1024000,
    "file_type": "pdf"
  },
  {
    "success": true,
    "message": "文件上传成功",
    "filename": "image.png",
    "file_path": "uploads/20231201_143023_b2c3d4e5_image.png",
    "file_size": 512000,
    "file_type": "png"
  }
]
```

## 使用示例

### Python (requests)

```python
import requests

# 单文件上传
url = "http://localhost:8000/api/upload/"
files = {'file': open('example.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())

# 批量上传
url = "http://localhost:8000/api/upload/multiple"
files = [
    ('files', open('file1.pdf', 'rb')),
    ('files', open('file2.docx', 'rb')),
    ('files', open('image.png', 'rb'))
]
response = requests.post(url, files=files)
print(response.json())
```

### JavaScript (fetch)

```javascript
// 单文件上传
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/upload/', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('上传成功:', data);
  console.log('文件路径:', data.file_path);
})
.catch(error => console.error('上传失败:', error));

// 批量上传
const formData = new FormData();
for (let file of fileInput.files) {
  formData.append('files', file);
}

fetch('http://localhost:8000/api/upload/multiple', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('批量上传结果:', data);
});
```

### cURL

```bash
# 单文件上传
curl -X POST "http://localhost:8000/api/upload/" \
  -F "file=@example.pdf"

# 批量上传
curl -X POST "http://localhost:8000/api/upload/multiple" \
  -F "files=@file1.pdf" \
  -F "files=@file2.docx" \
  -F "files=@image.png"
```

## 文件命名规则

上传的文件会自动重命名为以下格式：
```
{时间戳}_{UUID}_{原文件名}.{扩展名}
```

例如：
- 原文件名: `我的文档.pdf`
- 保存为: `20231201_143022_a1b2c3d4_我的文档.pdf`

这样可以：
1. 避免文件名冲突
2. 保留原始文件名信息
3. 便于按时间排序

## 文件存储

- 所有上传的文件保存在 `backend/uploads/` 目录
- 文件路径以相对路径形式返回（相对于项目根目录）
- 可以通过 `http://localhost:8000/uploads/{filename}` 访问文件（如果配置了静态文件服务）

## 错误处理

API会返回以下错误：

1. **400 Bad Request**: 
   - 文件类型不支持
   - 文件大小超过限制
   - 文件为空

2. **500 Internal Server Error**:
   - 文件保存失败
   - 服务器内部错误

## 安全特性

1. **文件类型验证**: 只允许指定的文件类型
2. **文件大小限制**: 防止上传过大文件
3. **文件名清理**: 移除特殊字符，防止路径遍历攻击
4. **唯一文件名**: 使用时间戳和UUID避免文件名冲突

## 注意事项

1. 确保 `uploads` 目录有写入权限
2. 定期清理旧文件，避免磁盘空间不足
3. 生产环境建议添加身份验证
4. 可以考虑添加文件病毒扫描功能
5. 大文件上传建议使用分片上传






