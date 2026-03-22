"""
文档解析模块测试示例
"""
import os
from app.utils.document_parser import (
    parse_document,
    parse_pdf,
    parse_word,
    parse_ppt,
    get_document_info
)


def test_parse_pdf(file_path: str):
    """测试PDF解析"""
    print(f"\n=== 测试PDF解析: {file_path} ===")
    try:
        text, page_count = parse_pdf(file_path)
        print(f"页数: {page_count}")
        print(f"文本长度: {len(text)} 字符")
        print(f"前500字符预览:\n{text[:500]}...")
    except Exception as e:
        print(f"错误: {e}")


def test_parse_word(file_path: str):
    """测试Word解析"""
    print(f"\n=== 测试Word解析: {file_path} ===")
    try:
        text, page_count = parse_word(file_path)
        print(f"估算页数: {page_count}")
        print(f"文本长度: {len(text)} 字符")
        print(f"前500字符预览:\n{text[:500]}...")
    except Exception as e:
        print(f"错误: {e}")


def test_parse_ppt(file_path: str):
    """测试PPT解析"""
    print(f"\n=== 测试PPT解析: {file_path} ===")
    try:
        text, slide_count = parse_ppt(file_path)
        print(f"幻灯片数: {slide_count}")
        print(f"文本长度: {len(text)} 字符")
        print(f"前500字符预览:\n{text[:500]}...")
    except Exception as e:
        print(f"错误: {e}")


def test_parse_document(file_path: str):
    """测试统一解析接口"""
    print(f"\n=== 测试统一解析接口: {file_path} ===")
    try:
        text, page_count, doc_type = parse_document(file_path)
        print(f"文档类型: {doc_type}")
        print(f"页数/幻灯片数: {page_count}")
        print(f"文本长度: {len(text)} 字符")
        print(f"前500字符预览:\n{text[:500]}...")
    except Exception as e:
        print(f"错误: {e}")


def test_get_document_info(file_path: str):
    """测试获取文档信息"""
    print(f"\n=== 测试获取文档信息: {file_path} ===")
    try:
        info = get_document_info(file_path)
        print(f"文档信息: {info}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    # 测试文件路径（需要替换为实际文件）
    test_files = {
        'pdf': 'test.pdf',
        'word': 'test.docx',
        'ppt': 'test.pptx'
    }
    
    print("文档解析模块测试")
    print("=" * 50)
    
    # 测试统一接口
    for doc_type, file_path in test_files.items():
        if os.path.exists(file_path):
            test_parse_document(file_path)
            test_get_document_info(file_path)
        else:
            print(f"\n文件不存在: {file_path}，跳过测试")
    
    print("\n测试完成！")






