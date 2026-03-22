"""
文档解析模块使用示例
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.document_parser import (
    parse_document,
    parse_pdf,
    parse_word,
    parse_ppt,
    get_document_info
)


def example_parse_pdf():
    """PDF解析示例"""
    print("=" * 50)
    print("PDF解析示例")
    print("=" * 50)
    
    file_path = "uploads/example.pdf"  # 替换为实际文件路径
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        text, page_count = parse_pdf(file_path)
        print(f"✓ 成功解析PDF")
        print(f"  页数: {page_count}")
        print(f"  文本长度: {len(text)} 字符")
        print(f"\n文本预览（前300字符）:")
        print("-" * 50)
        print(text[:300])
        print("-" * 50)
    except Exception as e:
        print(f"✗ 解析失败: {e}")


def example_parse_word():
    """Word文档解析示例"""
    print("\n" + "=" * 50)
    print("Word文档解析示例")
    print("=" * 50)
    
    file_path = "uploads/example.docx"  # 替换为实际文件路径
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        text, page_count = parse_word(file_path)
        print(f"✓ 成功解析Word文档")
        print(f"  估算页数: {page_count}")
        print(f"  文本长度: {len(text)} 字符")
        print(f"\n文本预览（前300字符）:")
        print("-" * 50)
        print(text[:300])
        print("-" * 50)
    except Exception as e:
        print(f"✗ 解析失败: {e}")


def example_parse_ppt():
    """PPT解析示例"""
    print("\n" + "=" * 50)
    print("PPT解析示例")
    print("=" * 50)
    
    file_path = "uploads/example.pptx"  # 替换为实际文件路径
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        text, slide_count = parse_ppt(file_path)
        print(f"✓ 成功解析PPT")
        print(f"  幻灯片数: {slide_count}")
        print(f"  文本长度: {len(text)} 字符")
        print(f"\n文本预览（前300字符）:")
        print("-" * 50)
        print(text[:300])
        print("-" * 50)
    except Exception as e:
        print(f"✗ 解析失败: {e}")


def example_unified_parser():
    """统一解析接口示例"""
    print("\n" + "=" * 50)
    print("统一解析接口示例")
    print("=" * 50)
    
    # 测试不同格式的文件
    test_files = [
        "uploads/example.pdf",
        "uploads/example.docx",
        "uploads/example.pptx"
    ]
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"\n跳过不存在的文件: {file_path}")
            continue
        
        try:
            text, page_count, doc_type = parse_document(file_path)
            print(f"\n✓ {file_path}")
            print(f"  类型: {doc_type}")
            print(f"  页数/幻灯片数: {page_count}")
            print(f"  文本长度: {len(text)} 字符")
        except Exception as e:
            print(f"\n✗ {file_path}: {e}")


def example_get_info():
    """获取文档信息示例"""
    print("\n" + "=" * 50)
    print("获取文档信息示例")
    print("=" * 50)
    
    file_path = "uploads/example.pdf"  # 替换为实际文件路径
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        info = get_document_info(file_path)
        print(f"文档信息:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"✗ 获取信息失败: {e}")


def example_save_extracted_text():
    """保存提取的文本示例"""
    print("\n" + "=" * 50)
    print("保存提取的文本示例")
    print("=" * 50)
    
    file_path = "uploads/example.pdf"  # 替换为实际文件路径
    output_path = "extracted_text.txt"
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    try:
        text, page_count, doc_type = parse_document(file_path)
        
        # 保存提取的文本
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"文档类型: {doc_type}\n")
            f.write(f"页数/幻灯片数: {page_count}\n")
            f.write("=" * 50 + "\n\n")
            f.write(text)
        
        print(f"✓ 文本已保存到: {output_path}")
        print(f"  文档类型: {doc_type}")
        print(f"  页数: {page_count}")
        print(f"  文本长度: {len(text)} 字符")
    except Exception as e:
        print(f"✗ 处理失败: {e}")


if __name__ == "__main__":
    print("\n文档解析模块使用示例\n")
    
    # 运行各个示例
    example_parse_pdf()
    example_parse_word()
    example_parse_ppt()
    example_unified_parser()
    example_get_info()
    example_save_extracted_text()
    
    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)






