# OCR识别模块文档

## 概述

OCR识别模块使用PaddleOCR和OpenCV实现图片文字识别功能。

### 使用的库

- **PaddleOCR**: 百度开源OCR工具，支持中英文识别，识别准确率高
- **OpenCV**: 图像预处理，提高OCR识别准确率

## 功能特性

### 1. 核心功能

- ✅ **输入图片**: 支持多种图片格式（JPG, PNG, GIF, BMP, WEBP, TIFF等）
- ✅ **自动识别文字**: 使用PaddleOCR自动识别图片中的文字
- ✅ **输出文本**: 返回识别出的文本内容

### 2. 高级功能

- **图像预处理**: 使用OpenCV进行灰度化、二值化、降噪等处理，提高识别准确率
- **详细结果**: 返回每行文字的坐标、置信度等详细信息
- **批量识别**: 支持同时识别多张图片
- **中英文混合**: 默认支持中英文混合识别

## API参考

### 工具函数

#### `extract_text_from_image(image_path: str, use_preprocess: bool = True) -> str`

简单OCR识别，只返回文本内容。

**参数**:
- `image_path`: 图片文件路径
- `use_preprocess`: 是否使用OpenCV预处理（默认True）

**返回**: 识别出的文本内容（字符串）

**示例**:
```python
from app.utils.ocr import extract_text_from_image

text = extract_text_from_image("image.png")
print(text)
```

#### `extract_text_from_image_detailed(image_path: str, use_preprocess: bool = True) -> Dict`

详细OCR识别，返回完整信息。

**返回字典包含**:
- `text`: 完整文本内容
- `details`: 详细信息列表，每个元素包含：
  - `text`: 该行文字
  - `confidence`: 置信度（0-1）
  - `bbox`: 文字框坐标
- `confidence`: 平均置信度
- `line_count`: 文本行数

**示例**:
```python
from app.utils.ocr import extract_text_from_image_detailed

result = extract_text_from_image_detailed("image.png")
print(f"文本: {result['text']}")
print(f"置信度: {result['confidence']:.2%}")
print(f"行数: {result['line_count']}")
```

#### `extract_text_from_multiple_images(image_paths: List[str], use_preprocess: bool = True) -> List[Dict]`

批量识别多张图片。

**参数**:
- `image_paths`: 图片路径列表
- `use_preprocess`: 是否使用预处理

**返回**: 识别结果列表

**示例**:
```python
from app.utils.ocr import extract_text_from_multiple_images

results = extract_text_from_multiple_images(["img1.png", "img2.jpg"])
for result in results:
    if result['success']:
        print(f"{result['image_path']}: {result['text']}")
```

### OCRProcessor类

高级用法，可以自定义OCR配置。

```python
from app.utils.ocr import OCRProcessor

# 创建OCR处理器
processor = OCRProcessor(
    use_angle_cls=True,  # 使用角度分类器
    lang='ch'  # 语言：'ch'中文，'en'英文
)

# 识别文字
result = processor.recognize_text("image.png")
print(result['text'])
```

## API端点

### 1. 简单OCR识别

**端点**: `POST /api/ocr/recognize-simple`

**请求**: `multipart/form-data`

**参数**:
- `file`: 图片文件
- `use_preprocess`: 是否预处理（可选，默认true）

**响应**:
```json
{
  "success": true,
  "text": "识别出的文本内容",
  "filename": "image.png"
}
```

### 2. 详细OCR识别

**端点**: `POST /api/ocr/recognize`

**请求**: `multipart/form-data`

**参数**:
- `file`: 图片文件
- `use_preprocess`: 是否预处理（可选，默认true）

**响应**:
```json
{
  "success": true,
  "text": "识别出的文本内容",
  "confidence": 0.95,
  "line_count": 10,
  "details": [
    {
      "text": "第一行文字",
      "confidence": 0.98,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ],
  "filename": "image.png"
}
```

### 3. 批量OCR识别

**端点**: `POST /api/ocr/recognize-batch`

**请求**: `multipart/form-data`

**参数**:
- `files`: 图片文件列表（多个文件）
- `use_preprocess`: 是否预处理（可选，默认true）

**响应**:
```json
[
  {
    "success": true,
    "text": "识别出的文本",
    "confidence": 0.95,
    "filename": "image1.png"
  },
  {
    "success": true,
    "text": "识别出的文本",
    "confidence": 0.92,
    "filename": "image2.jpg"
  }
]
```

## 使用示例

### Python (requests)

```python
import requests

# 简单识别
url = "http://localhost:8000/api/ocr/recognize-simple"
files = {'file': open('image.png', 'rb')}
response = requests.post(url, files=files)
print(response.json()['text'])

# 详细识别
url = "http://localhost:8000/api/ocr/recognize"
files = {'file': open('image.png', 'rb')}
data = {'use_preprocess': 'true'}
response = requests.post(url, files=files, data=data)
result = response.json()
print(f"文本: {result['text']}")
print(f"置信度: {result['confidence']:.2%}")
```

### JavaScript (fetch)

```javascript
// 简单识别
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/ocr/recognize-simple', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('识别文本:', data.text);
})
.catch(error => console.error('识别失败:', error));

// 详细识别
fetch('http://localhost:8000/api/ocr/recognize', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('文本:', data.text);
  console.log('置信度:', data.confidence);
  console.log('行数:', data.line_count);
});
```

### cURL

```bash
# 简单识别
curl -X POST "http://localhost:8000/api/ocr/recognize-simple" \
  -F "file=@image.png"

# 详细识别
curl -X POST "http://localhost:8000/api/ocr/recognize" \
  -F "file=@image.png" \
  -F "use_preprocess=true"

# 批量识别
curl -X POST "http://localhost:8000/api/ocr/recognize-batch" \
  -F "files=@image1.png" \
  -F "files=@image2.jpg"
```

## 图像预处理

OpenCV预处理包括以下步骤：

1. **灰度化**: 将彩色图片转换为灰度图
2. **二值化**: 使用OTSU算法进行自适应二值化
3. **降噪**: 使用非局部均值降噪算法

这些预处理步骤可以显著提高OCR识别准确率，特别是对于：
- 低对比度图片
- 有噪声的图片
- 扫描件图片

## 性能优化

### 1. 首次运行

PaddleOCR首次运行时会自动下载模型文件（约100-200MB），需要一些时间。

### 2. GPU加速

如果有NVIDIA GPU，可以启用GPU加速：

```python
processor = OCRProcessor()
processor.ocr = PaddleOCR(use_gpu=True)  # 启用GPU
```

### 3. 批量处理

批量识别时，OCR处理器会复用，避免重复初始化。

## 支持的图片格式

- `.jpg`, `.jpeg`: JPEG格式
- `.png`: PNG格式
- `.gif`: GIF格式
- `.bmp`: BMP格式
- `.webp`: WebP格式
- `.tiff`, `.tif`: TIFF格式

## 错误处理

常见错误及解决方法：

1. **ImportError**: 未安装依赖库
   ```bash
   pip install paddlepaddle paddleocr opencv-python Pillow
   ```

2. **FileNotFoundError**: 图片文件不存在
   - 检查文件路径是否正确

3. **识别失败**: 图片格式不支持或损坏
   - 确认图片格式在支持列表中
   - 尝试使用其他图片

## 注意事项

1. **模型下载**: 首次使用会自动下载模型，需要网络连接
2. **内存占用**: PaddleOCR需要一定内存，建议至少2GB可用内存
3. **识别速度**: 预处理会稍微增加处理时间，但能提高准确率
4. **中文支持**: 默认支持中英文混合识别，无需额外配置

## 依赖安装

```bash
pip install paddlepaddle paddleocr opencv-python Pillow
```

## 示例代码

完整示例请参考 `test_ocr.py` 文件。






