"""
OCR识别工具
使用 EasyOCR（优先，支持 Torch CUDA GPU）或 PaddleOCR（可选）进行文字识别

功能：
1. 输入图片
2. 自动识别文字
3. 输出文本
"""
from typing import Optional, List, Tuple, Dict, Any
import os
import numpy as np
from pathlib import Path

try:
    import cv2
except ImportError as e:
    print("警告: OpenCV未安装，请运行 pip install opencv-python")
    print(f"错误详情: {e}")
    cv2 = None

# 注意：不要在模块 import 时直接 import paddleocr（你当前环境里 Paddle 相关二进制可能触发 SIGILL）。
# PaddleOCR / EasyOCR 都采用“懒加载”方式：仅在真正初始化对应引擎时才 import。


def _torch_cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def _to_json_safe(value: Any) -> Any:
    """将 numpy/数组等对象转换为 JSON 可序列化的原生类型。"""
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]
    return value


class OCRProcessor:
    """
    OCR处理器（统一接口）

    默认优先使用 EasyOCR（支持 Torch CUDA GPU），可通过环境变量切换：
    - OCR_ENGINE=easyocr | paddle
    - OCR_USE_GPU=true/false（仅对支持 GPU 的引擎生效）
    """
    
    def __init__(self, use_angle_cls: bool = True, lang: str = 'ch', use_gpu: Optional[bool] = None):
        """
        初始化OCR处理器
        
        Args:
            use_angle_cls: 是否使用角度分类器（用于检测文字方向）
            lang: 识别语言，'ch'中文，'en'英文，'ch'默认支持中英文混合
            use_gpu: 是否使用GPU（None表示自动：paddle编译支持CUDA则用GPU，否则CPU）
        """
        if cv2 is None:
            raise ImportError("OpenCV未安装，请运行 pip install opencv-python")

        self.lang = lang
        self.use_angle_cls = use_angle_cls

        # 允许环境变量强制覆盖（便于排错/部署）
        env_force = os.getenv("OCR_USE_GPU")
        if env_force is not None:
            use_gpu = env_force.strip().lower() in {"1", "true", "yes", "y"}

        engine = (os.getenv("OCR_ENGINE") or "easyocr").strip().lower()
        if engine not in {"easyocr", "paddle"}:
            engine = "easyocr"

        self.engine = engine
        self.use_gpu = bool(use_gpu) if use_gpu is not None else _torch_cuda_available()

        if self.engine == "easyocr":
            self._init_easyocr()
        else:
            self._init_paddleocr()

    def _init_easyocr(self):
        try:
            import easyocr
        except Exception as e:
            raise ImportError(f"EasyOCR未安装或导入失败: {e}. 请运行: pip install easyocr")

        # EasyOCR 语言：中文简体+英文更符合常见学习资料
        langs = ["ch_sim", "en"] if self.lang == "ch" else ["en"]
        # gpu=True 需要 torch.cuda 可用；若 GPU 初始化失败则自动回退到 CPU。
        gpu_flag = bool(self.use_gpu and _torch_cuda_available())
        if gpu_flag:
            try:
                self.reader = easyocr.Reader(langs, gpu=True)
                self.use_gpu = True
                return
            except Exception as e:
                print(f"OCR GPU 初始化失败，自动回退 CPU: {e}")

        self.reader = easyocr.Reader(langs, gpu=False)
        self.use_gpu = False

    def _init_paddleocr(self):
        # 懒加载 import，避免在环境不兼容时拖垮整个后端
        try:
            from paddleocr import PaddleOCR
            import paddle
        except Exception as e:
            raise ImportError(f"PaddleOCR未安装或导入失败: {e}.")

        # paddle 是否支持 CUDA 决定是否真的能用 GPU
        paddle_gpu_ok = False
        try:
            paddle_gpu_ok = bool(paddle.is_compiled_with_cuda())
        except Exception:
            paddle_gpu_ok = False

        self.ocr = PaddleOCR(
            use_angle_cls=self.use_angle_cls,
            lang=self.lang,
            use_gpu=bool(self.use_gpu and paddle_gpu_ok),
        )
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        使用OpenCV预处理图片，提高OCR识别准确率
        
        Args:
            image_path: 图片路径
        
        Returns:
            预处理后的图片数组
        """
        if cv2 is None:
            raise ImportError("OpenCV未安装，请运行 pip install opencv-python")
        
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        # 转换为灰度图
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # 二值化处理（提高对比度）
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 降噪处理
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def recognize_text(self, image_path: str, use_preprocess: bool = True) -> Dict[str, Any]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片路径
            use_preprocess: 是否使用OpenCV预处理（默认True）
        
        Returns:
            包含识别结果的字典：
            {
                'text': 完整文本,
                'details': 详细信息列表（每行文字及其坐标和置信度）
            }
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        try:
            # 预处理失败时自动降级为原图，避免直接报 500
            if use_preprocess:
                try:
                    img = self.preprocess_image(image_path)
                except Exception as preprocess_error:
                    print(f"OCR预处理失败，改用原图: {preprocess_error}")
                    img = cv2.imread(image_path)
            else:
                img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"无法读取图片: {image_path}")

            if self.engine == "easyocr":
                # EasyOCR 输出: [ [bbox, text, conf], ... ]
                results = self.reader.readtext(img)
                text_lines: List[str] = []
                details: List[Dict[str, Any]] = []
                total_conf = 0.0
                valid = 0
                for item in results:
                    if not item or len(item) < 3:
                        continue
                    bbox, text, conf = item[0], item[1], float(item[2])
                    if text:
                        text_lines.append(str(text))
                        details.append(
                            {
                                "text": str(text),
                                "confidence": float(conf),
                                "bbox": _to_json_safe(bbox),
                            }
                        )
                        total_conf += conf
                        valid += 1
                full_text = "\n".join(text_lines).strip()
                avg_conf = total_conf / valid if valid else 0.0
                return {
                    "text": full_text,
                    "details": _to_json_safe(details),
                    "confidence": float(avg_conf),
                    "line_count": int(len(text_lines)),
                }

            # PaddleOCR 分支（兼容保留）
            result = self.ocr.ocr(img if use_preprocess else image_path, cls=True)
            if result is None or len(result) == 0 or result[0] is None:
                return {"text": "", "details": [], "confidence": 0.0, "line_count": 0}
            
            text_lines: List[str] = []
            details: List[Dict[str, Any]] = []
            total_confidence = 0.0
            valid_count = 0
            for line in result[0]:
                if line is None:
                    continue
                box = line[0]
                text_info = line[1]
                if text_info:
                    text = text_info[0]
                    confidence = float(text_info[1])
                    text_lines.append(text)
                    details.append(
                        {
                            "text": str(text),
                            "confidence": float(confidence),
                            "bbox": _to_json_safe(box),
                        }
                    )
                    total_confidence += confidence
                    valid_count += 1
            full_text = "\n".join(text_lines).strip()
            avg_confidence = total_confidence / valid_count if valid_count > 0 else 0.0
            return {
                "text": full_text,
                "details": _to_json_safe(details),
                "confidence": float(avg_confidence),
                "line_count": int(len(text_lines)),
            }
        
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def recognize_text_simple(self, image_path: str, use_preprocess: bool = True) -> str:
        """
        简化版文字识别，只返回文本内容
        
        Args:
            image_path: 图片路径
            use_preprocess: 是否使用OpenCV预处理
        
        Returns:
            识别出的文本内容
        """
        result = self.recognize_text(image_path, use_preprocess)
        return result['text']


# 全局OCR处理器实例（懒加载）
_ocr_processor: Optional[OCRProcessor] = None


def get_ocr_processor() -> OCRProcessor:
    """
    获取全局OCR处理器实例（单例模式）
    
    Returns:
        OCRProcessor实例
    """
    global _ocr_processor
    if _ocr_processor is None:
        _ocr_processor = OCRProcessor()
    return _ocr_processor


def reset_ocr_processor() -> None:
    """重置全局 OCR 实例（用于运行期异常后的自恢复重试）。"""
    global _ocr_processor
    _ocr_processor = None


def extract_text_from_image(image_path: str, use_preprocess: bool = True) -> str:
    """
    从图片中提取文本（OCR）
    
    这是主要的OCR接口函数
    
    Args:
        image_path: 图片路径
        use_preprocess: 是否使用OpenCV预处理图片（默认True，可提高识别准确率）
    
    Returns:
        提取的文本内容
    
    Examples:
        >>> text = extract_text_from_image("image.png")
        >>> print(text)
    """
    processor = get_ocr_processor()
    return processor.recognize_text_simple(image_path, use_preprocess)


def extract_text_from_image_detailed(image_path: str, use_preprocess: bool = True) -> Dict[str, Any]:
    """
    从图片中提取文本（OCR），返回详细信息
    
    Args:
        image_path: 图片路径
        use_preprocess: 是否使用OpenCV预处理
    
    Returns:
        包含文本和详细信息的字典：
        {
            'text': 完整文本,
            'details': 详细信息列表,
            'confidence': 平均置信度,
            'line_count': 文本行数
        }
    """
    processor = get_ocr_processor()
    return processor.recognize_text(image_path, use_preprocess)


def extract_text_from_multiple_images(image_paths: List[str], use_preprocess: bool = True) -> List[Dict[str, Any]]:
    """
    批量识别多张图片中的文字
    
    Args:
        image_paths: 图片路径列表
        use_preprocess: 是否使用OpenCV预处理
    
    Returns:
        识别结果列表，每个元素包含一张图片的识别结果
    """
    processor = get_ocr_processor()
    results = []
    
    for image_path in image_paths:
        try:
            result = processor.recognize_text(image_path, use_preprocess)
            result['image_path'] = image_path
            result['success'] = True
        except Exception as e:
            result = {
                'image_path': image_path,
                'success': False,
                'error': str(e),
                'text': '',
                'details': [],
                'confidence': 0.0
            }
        
        results.append(result)
    
    return results


def extract_text_from_pdf_images(pdf_path: str) -> Optional[str]:
    """
    从PDF中提取图片并进行OCR识别
    
    注意：需要先使用pdf2image将PDF转换为图片
    
    Args:
        pdf_path: PDF文件路径
    
    Returns:
        提取的文本内容（如果PDF中没有图片则返回None）
    
    TODO: 实现PDF图片提取功能
    """
    # 这里需要先提取PDF中的图片，然后进行OCR
    # 可以使用pdf2image库将PDF页面转换为图片
    # 由于依赖较多，这里仅提供接口
    pass

