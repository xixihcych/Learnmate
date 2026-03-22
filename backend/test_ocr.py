"""
OCR识别模块测试示例
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils.ocr import (
    extract_text_from_image,
    extract_text_from_image_detailed,
    extract_text_from_multiple_images,
    OCRProcessor
)


def test_simple_ocr(image_path: str):
    """测试简单OCR识别"""
    print(f"\n=== 测试简单OCR识别: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        return
    
    try:
        text = extract_text_from_image(image_path)
        print(f"✓ 识别成功")
        print(f"识别文本:\n{text}")
    except Exception as e:
        print(f"✗ 识别失败: {e}")


def test_detailed_ocr(image_path: str):
    """测试详细OCR识别"""
    print(f"\n=== 测试详细OCR识别: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        return
    
    try:
        result = extract_text_from_image_detailed(image_path)
        print(f"✓ 识别成功")
        print(f"文本内容:\n{result['text']}")
        print(f"平均置信度: {result['confidence']:.2%}")
        print(f"文本行数: {result['line_count']}")
        print(f"\n详细信息（前3行）:")
        for i, detail in enumerate(result['details'][:3], 1):
            print(f"  行{i}: {detail['text']} (置信度: {detail['confidence']:.2%})")
    except Exception as e:
        print(f"✗ 识别失败: {e}")


def test_batch_ocr(image_paths: list):
    """测试批量OCR识别"""
    print(f"\n=== 测试批量OCR识别 ===")
    
    existing_paths = [p for p in image_paths if os.path.exists(p)]
    
    if not existing_paths:
        print("没有找到有效的图片文件")
        return
    
    try:
        results = extract_text_from_multiple_images(existing_paths)
        
        for i, result in enumerate(results, 1):
            print(f"\n图片 {i}: {result.get('image_path', '未知')}")
            if result['success']:
                print(f"  ✓ 识别成功")
                print(f"  文本长度: {len(result['text'])} 字符")
                print(f"  置信度: {result['confidence']:.2%}")
                print(f"  文本预览: {result['text'][:100]}...")
            else:
                print(f"  ✗ 识别失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"✗ 批量识别失败: {e}")


def test_with_preprocess(image_path: str):
    """测试使用和不使用预处理的对比"""
    print(f"\n=== 测试预处理效果对比: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"文件不存在: {image_path}")
        return
    
    try:
        # 不使用预处理
        print("\n不使用预处理:")
        result1 = extract_text_from_image_detailed(image_path, use_preprocess=False)
        print(f"  文本长度: {len(result1['text'])} 字符")
        print(f"  置信度: {result1['confidence']:.2%}")
        
        # 使用预处理
        print("\n使用预处理:")
        result2 = extract_text_from_image_detailed(image_path, use_preprocess=True)
        print(f"  文本长度: {len(result2['text'])} 字符")
        print(f"  置信度: {result2['confidence']:.2%}")
        
        print("\n对比:")
        if result2['confidence'] > result1['confidence']:
            print("  ✓ 预处理提高了识别准确率")
        else:
            print("  - 预处理效果不明显")
    
    except Exception as e:
        print(f"✗ 测试失败: {e}")


if __name__ == "__main__":
    print("OCR识别模块测试")
    print("=" * 50)
    
    # 测试文件路径（需要替换为实际文件）
    test_image = "test_image.png"
    
    if os.path.exists(test_image):
        test_simple_ocr(test_image)
        test_detailed_ocr(test_image)
        test_with_preprocess(test_image)
    else:
        print(f"\n测试文件不存在: {test_image}")
        print("请将测试图片放在项目根目录，或修改test_image变量")
    
    # 批量测试
    test_images = ["test1.png", "test2.jpg", "test3.png"]
    test_batch_ocr(test_images)
    
    print("\n" + "=" * 50)
    print("测试完成！")






