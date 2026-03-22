# 文档解析模块文档

## 概述

文档解析模块提供统一的文档解析功能，支持PDF、Word、PPT格式，输出统一的文本格式。

## 使用的库

- **pdfplumber**: PDF文档解析（替代PyPDF2，提供更好的文本提取能力）
- **python-docx**: Word文档解析
- **python-pptx**: PPT文档解析

## 功能特性

### 1. 支持的格式

- **PDF** (`.pdf`): 支持文本和表格提取
- **Word** (`.doc`, `.docx`): 支持段落和表格提取
- **PPT** (`.ppt`, `.pptx`): 支持幻灯片文本和表格提取

### 2. 统一输出格式

所有文档类型都输出统一的文本格式：
- 清理多余的空白字符
- 统一段落分隔
- 保留页面/幻灯片标记
- 表格格式化为文本

### 3. 文本清理

自动执行以下清理操作：
- 移除多余的空白字符
- 统一换行符
- 移除首尾空白
- 过滤空内容

## API参考

### 主要函数

#### `parse_document(file_path: str) -> Tuple[str, int, str]`

统一文档解析入口，根据文件扩展名自动选择解析器。

**参数**:
- `file_path`: 文档文件路径

**返回**:
- `text`: 提取的文本内容
- `page_count`: 页数或幻灯片数
- `doc_type`: 文档类型（'pdf', 'word', 'ppt'）

**示例**:
```python
from app.utils.document_parser import parse_document

text, pages, doc_type = parse_document("example.pdf")
print(f"提取了 {pages} 页内容")
print(f"文档类型: {doc_type}")
```

#### `parse_pdf(file_path: str) -> Tuple[str, int]`

解析PDF文件。

**特性**:
- 提取每页文本
- 提取表格内容
- 添加页面标记

**示例**:
```python
from app.utils.document_parser import parse_pdf

text, page_count = parse_pdf("document.pdf")
```

#### `parse_word(file_path: str) -> Tuple[str, int]`

解析Word文档。

**特性**:
- 提取段落文本
- 提取表格内容
- 估算页数（每页约500字）

**示例**:
```python
from app.utils.document_parser import parse_word

text, page_count = parse_word("document.docx")
```

#### `parse_ppt(file_path: str) -> Tuple[str, int]`

解析PPT文件。

**特性**:
- 提取每张幻灯片的文本
- 提取表格内容
- 添加幻灯片标记

**示例**:
```python
from app.utils.document_parser import parse_ppt

text, slide_count = parse_ppt("presentation.pptx")
```

#### `get_document_info(file_path: str) -> Dict[str, any]`

获取文档基本信息。

**返回的字典包含**:
- `filename`: 文件名
- `file_type`: 文件扩展名
- `file_size`: 文件大小（字节）
- `exists`: 文件是否存在
- `page_count`: 页数（如果可解析）
- `document_type`: 文档类型（如果可解析）

**示例**:
```python
from app.utils.document_parser import get_document_info

info = get_document_info("example.pdf")
print(f"文件名: {info['filename']}")
print(f"页数: {info.get('page_count', '未知')}")
```

## 输出格式示例

### PDF输出格式

```
=== 第 1 页 ===
这是第一页的内容...

=== 第 2 页 ===
这是第二页的内容...

--- 第 2 页 表格 1 ---
列1 | 列2 | 列3
值1 | 值2 | 值3
```

### Word输出格式

```
第一段内容...

第二段内容...

--- 表格 1 ---
列1 | 列2 | 列3
值1 | 值2 | 值3
```

### PPT输出格式

```
=== 幻灯片 1 ===
标题文本
内容文本

=== 幻灯片 2 ===
标题文本
表格:
列1 | 列2
值1 | 值2
```

## 使用示例

### 基本使用

```python
from app.utils.document_parser import parse_document

# 解析任意支持的文档类型
text, pages, doc_type = parse_document("document.pdf")

# 保存提取的文本
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

### 批量处理

```python
import os
from app.utils.document_parser import parse_document

documents = ["doc1.pdf", "doc2.docx", "doc3.pptx"]

for doc_path in documents:
    if os.path.exists(doc_path):
        try:
            text, pages, doc_type = parse_document(doc_path)
            print(f"{doc_path}: {pages} 页，{len(text)} 字符")
        except Exception as e:
            print(f"{doc_path}: 解析失败 - {e}")
```

### 在FastAPI路由中使用

```python
from fastapi import APIRouter, HTTPException
from app.utils.document_parser import parse_document

router = APIRouter()

@router.post("/parse")
async def parse_document_endpoint(file_path: str):
    try:
        text, pages, doc_type = parse_document(file_path)
        return {
            "success": True,
            "text": text,
            "page_count": pages,
            "document_type": doc_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 错误处理

所有解析函数在遇到错误时会抛出异常：

- `FileNotFoundError`: 文件不存在
- `ValueError`: 不支持的文件类型
- `Exception`: 解析过程中的其他错误

**建议的错误处理**:

```python
from app.utils.document_parser import parse_document

try:
    text, pages, doc_type = parse_document("document.pdf")
except FileNotFoundError:
    print("文件不存在")
except ValueError as e:
    print(f"不支持的文件类型: {e}")
except Exception as e:
    print(f"解析失败: {e}")
```

## 性能考虑

1. **大文件处理**: 对于非常大的PDF文件，pdfplumber可能需要较长时间
2. **内存使用**: 解析大文件时注意内存占用
3. **并发处理**: 可以使用后台任务处理大文件解析

## 依赖安装

```bash
pip install pdfplumber python-docx python-pptx
```

## 注意事项

1. **PDF解析**: pdfplumber比PyPDF2更准确，但可能稍慢
2. **Word表格**: 表格会被转换为文本格式，使用 `|` 分隔列
3. **PPT格式**: 只提取文本内容，不包含图片和图表
4. **编码**: 所有文本输出使用UTF-8编码
5. **页数估算**: Word文档的页数是估算值（每页约500字）

## 扩展性

如果需要添加新的文档类型支持，可以：

1. 在 `parse_document()` 函数中添加新的文件类型判断
2. 实现对应的解析函数（如 `parse_excel()`）
3. 使用 `DocumentParser.format_output()` 统一输出格式






