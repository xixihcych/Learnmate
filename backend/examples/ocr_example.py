"""
OCR识别模块使用示例
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.ocr import (
    extract_text_from_image,
    extract_text_from_image_detailed,
    extract_text_from_multiple_images,
    OCRProcessor
)


def example_simple_ocr():
    """简单OCR识别示例"""
    print("=" * 50)
    print("简单OCR识别示例")
    print("=" * 50)
    
    image_path = "uploads/test_image.png"  # 替换为实际图片路径
    
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        print("请将测试图片放在 uploads 目录下")
        return
    
    try:
        text = extract_text_from_image(image_path)
        print(f"✓ 识别成功")
        print(f"\n识别文本:\n{text}")
    except Exception as e:
        print(f"✗ 识别失败: {e}")


def example_detailed_ocr():
    """详细OCR识别示例"""
    print("\n" + "=" * 50)
    print("详细OCR识别示例")
    print("=" * 50)
    
    image_path = "uploads/test_image.png"
    
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        return
    
    try:
        result = extract_text_from_image_detailed(image_path)
        
        print(f"✓ 识别成功")
        print(f"\n文本内容:")
        print("-" * 50)
        print(result['text'])
        print("-" * 50)
        print(f"\n统计信息:")
        print(f"  平均置信度: {result['confidence']:.2%}")
        print(f"  文本行数: {result['line_count']}")
        print(f"\n详细信息（前5行）:")
        for i, detail in enumerate(result['details'][:5], 1):
            print(f"  行{i}: {detail['text']}")
            print(f"      置信度: {detail['confidence']:.2%}")
    except Exception as e:
        print(f"✗ 识别失败: {e}")


def example_batch_ocr():
    """批量OCR识别示例"""
    print("\n" + "=" * 50)
    print("批量OCR识别示例")
    print("=" * 50)
    
    image_paths = [
        "uploads/image1.png",
        "uploads/image2.jpg",
        "uploads/image3.png"
    ]
    
    # 过滤存在的文件
    existing_paths = [p for p in image_paths if os.path.exists(p)]
    
    if not existing_paths:
        print("没有找到测试图片")
        return
    
    try:
        results = extract_text_from_multiple_images(existing_paths)
        
        print(f"✓ 批量识别完成，共处理 {len(results)} 张图片\n")
        
        for i, result in enumerate(results, 1):
            print(f"图片 {i}: {os.path.basename(result.get('image_path', '未知'))}")
            if result['success']:
                print(f"  ✓ 识别成功")
                print(f"  文本长度: {len(result['text'])} 字符")
                print(f"  置信度: {result['confidence']:.2%}")
                print(f"  文本预览: {result['text'][:100]}...")
            else:
                print(f"  ✗ 识别失败: {result.get('error', '未知错误')}")
            print()
    
    except Exception as e:
        print(f"✗ 批量识别失败: {e}")


def example_preprocess_comparison():
    """预处理效果对比示例"""
    print("\n" + "=" * 50)
    print("预处理效果对比示例")
    print("=" * 50)
    
    image_path = "uploads/test_image.png"
    
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        return
    
    try:
        print("\n1. 不使用预处理:")
        result1 = extract_text_from_image_detailed(image_path, use_preprocess=False)
        print(f"  文本长度: {len(result1['text'])} 字符")
        print(f"  置信度: {result1['confidence']:.2%}")
        print(f"  文本预览: {result1['text'][:100]}...")
        
        print("\n2. 使用预处理:")
        result2 = extract_text_from_image_detailed(image_path, use_preprocess=True)
        print(f"  文本长度: {len(result2['text'])} 字符")
        print(f"  置信度: {result2['confidence']:.2%}")
        print(f"  文本预览: {result2['text'][:100]}...")
        
        print("\n对比结果:")
        if result2['confidence'] > result1['confidence']:
            improvement = (result2['confidence'] - result1['confidence']) * 100
            print(f"  ✓ 预处理提高了 {improvement:.1f}% 的识别准确率")
        elif result2['confidence'] < result1['confidence']:
            print(f"  - 预处理效果不明显")
        else:
            print(f"  = 预处理效果相同")
    
    except Exception as e:
        print(f"✗ 对比测试失败: {e}")


def example_custom_processor():
    """自定义OCR处理器示例"""
    print("\n" + "=" * 50)
    print("自定义OCR处理器示例")
    print("=" * 50)
    
    image_path = "uploads/test_image.png"
    
    if not os.path.exists(image_path):
        print(f"图片不存在: {image_path}")
        return
    
    try:
        # 创建自定义OCR处理器
        processor = OCRProcessor(
            use_angle_cls=True,  # 使用角度分类器
            lang='ch'  # 中文（支持中英文混合）
        )
        
        print("✓ OCR处理器创建成功")
        
        # 识别文字
        result = processor.recognize_text(image_path, use_preprocess=True)
        
        print(f"\n识别结果:")
        print(f"  文本: {result['text'][:200]}...")
        print(f"  置信度: {result['confidence']:.2%}")
        print(f"  行数: {result['line_count']}")
    
    except Exception as e:
        print(f"✗ 处理失败: {e}")


if __name__ == "__main__":
    print("\nOCR识别模块使用示例\n")
    
    # 运行各个示例
    example_simple_ocr()
    example_detailed_ocr()
    example_batch_ocr()
    example_preprocess_comparison()
    example_custom_processor()
    
    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("=" * 50)
    print("\n提示:")
    print("- 首次运行会自动下载PaddleOCR模型（约100-200MB）")
    print("- 预处理可以提高识别准确率，特别是对于低质量图片")
    print("- 批量识别时，OCR处理器会复用，提高效率")






