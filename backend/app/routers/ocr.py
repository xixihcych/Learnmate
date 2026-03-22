"""
OCR识别路由
提供图片文字识别API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Optional, Tuple
import os
import tempfile
from pathlib import Path

from app.models import FileUploadResponse
from app.auth import CurrentUser, get_current_user_dep
from app.utils.ocr import (
    extract_text_from_image,
    extract_text_from_image_detailed,
    extract_text_from_multiple_images,
    reset_ocr_processor,
)

router = APIRouter()

# 支持的图片格式
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}


def _ocr_enabled() -> bool:
    return os.getenv("ENABLE_OCR", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """
    验证图片文件
    
    Returns:
        (is_valid, error_message)
    """
    if not file.filename:
        return False, "文件名不能为空"
    
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"不支持的图片格式: {file_ext}。支持的类型: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    return True, ""


def _run_ocr_with_retries(image_path: str, use_preprocess: bool):
    """
    OCR 兜底策略：
    1) 按用户设置尝试
    2) 关闭预处理重试
    3) 重置 OCR 引擎后再试（可修复首次初始化失败/模型状态异常）
    """
    errors = []

    try:
        return extract_text_from_image_detailed(image_path, use_preprocess=use_preprocess)
    except Exception as e:
        errors.append(f"首次识别失败: {e}")

    if use_preprocess:
        try:
            return extract_text_from_image_detailed(image_path, use_preprocess=False)
        except Exception as e:
            errors.append(f"关闭预处理重试失败: {e}")

    try:
        reset_ocr_processor()
        return extract_text_from_image_detailed(image_path, use_preprocess=False)
    except Exception as e:
        errors.append(f"重置OCR引擎后重试失败: {e}")
        raise Exception(" | ".join(errors))


@router.post("/recognize")
async def recognize_text_from_image(
    file: UploadFile = File(...),
    use_preprocess: bool = True,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    OCR文字识别API
    
    上传图片，自动识别其中的文字并返回文本内容
    
    Args:
        file: 上传的图片文件
        use_preprocess: 是否使用OpenCV预处理图片（默认True，可提高识别准确率）
    
    Returns:
        {
            "success": True,
            "text": "识别出的文本内容",
            "confidence": 0.95,
            "line_count": 10,
            "filename": "image.png"
        }
    """
    if not _ocr_enabled():
        raise HTTPException(
            status_code=400,
            detail="OCR 当前未启用（纯文本模式）。如需启用，请设置环境变量 ENABLE_OCR=true。",
        )

    # 验证文件
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 创建临时文件保存上传的图片
    file_ext = Path(file.filename).suffix.lower()
    temp_file = None
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file = tmp.name
            
            # 保存上传的文件
            content = await file.read()
            tmp.write(content)
        
        # 进行OCR识别（含多级兜底重试）
        try:
            result = _run_ocr_with_retries(temp_file, use_preprocess=use_preprocess)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")

        return {
            "success": True,
            "text": result['text'],
            "confidence": result['confidence'],
            "line_count": result['line_count'],
            "details": result['details'],
            "filename": file.filename
        }
    
    finally:
        # 清理临时文件
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@router.post("/recognize-simple")
async def recognize_text_simple(
    file: UploadFile = File(...),
    use_preprocess: bool = True,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    简化版OCR识别API
    
    只返回识别出的文本内容，不包含详细信息
    
    Args:
        file: 上传的图片文件
        use_preprocess: 是否使用OpenCV预处理
    
    Returns:
        {
            "success": True,
            "text": "识别出的文本内容",
            "filename": "image.png"
        }
    """
    if not _ocr_enabled():
        raise HTTPException(
            status_code=400,
            detail="OCR 当前未启用（纯文本模式）。如需启用，请设置环境变量 ENABLE_OCR=true。",
        )

    # 验证文件
    is_valid, error_msg = validate_image_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 创建临时文件
    file_ext = Path(file.filename).suffix.lower()
    temp_file = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file = tmp.name
            content = await file.read()
            tmp.write(content)
        
        # OCR识别（含多级兜底重试）
        try:
            result = _run_ocr_with_retries(temp_file, use_preprocess=use_preprocess)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")

        return {
            "success": True,
            "text": result["text"],
            "filename": file.filename
        }
    
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@router.post("/recognize-batch")
async def recognize_text_batch(
    files: List[UploadFile] = File(...),
    use_preprocess: bool = True,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    批量OCR识别API
    
    同时识别多张图片中的文字
    
    Args:
        files: 上传的图片文件列表
        use_preprocess: 是否使用OpenCV预处理
    
    Returns:
        识别结果列表，每个元素对应一张图片的识别结果
    """
    if not _ocr_enabled():
        raise HTTPException(
            status_code=400,
            detail="OCR 当前未启用（纯文本模式）。如需启用，请设置环境变量 ENABLE_OCR=true。",
        )

    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一张图片")
    
    results = []
    temp_files = []
    
    try:
        # 保存所有上传的文件到临时目录
        for file in files:
            is_valid, error_msg = validate_image_file(file)
            if not is_valid:
                results.append({
                    "success": False,
                    "filename": file.filename or "未知文件",
                    "error": error_msg,
                    "text": ""
                })
                continue
            
            file_ext = Path(file.filename).suffix.lower()
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
            temp_files.append(temp_file.name)
            
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
        
        # 批量识别
        if temp_files:
            batch_results = extract_text_from_multiple_images(temp_files, use_preprocess)
            
            # 匹配文件名
            file_index = 0
            for i, file in enumerate(files):
                is_valid, _ = validate_image_file(file)
                if is_valid:
                    if file_index < len(batch_results):
                        result = batch_results[file_index]
                        result['filename'] = file.filename
                        results.append(result)
                        file_index += 1
                else:
                    # 已经在上面处理过了
                    pass
        
        return results
    
    finally:
        # 清理临时文件
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

