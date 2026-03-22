"""
文件上传路由
支持PDF、PPT、Word、图片格式
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from typing import Tuple
import os
from pathlib import Path
from datetime import datetime
import uuid
import shutil

from app.models import FileUploadResponse, PathUploadRequest
from app.database import get_db_connection
from app.auth import CurrentUser, get_current_user_dep
from app.services.document_processor import process_document_by_id

router = APIRouter()

# 上传目录配置
UPLOAD_DIR = "uploads"

# 支持的文件类型
ALLOWED_EXTENSIONS = {
    # 文档类型
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    # 图片类型
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.bmp': 'image/bmp',
    '.webp': 'image/webp',
    '.tiff': 'image/tiff',
    '.tif': 'image/tiff',
}

# 最大文件大小（50MB）
MAX_FILE_SIZE = 50 * 1024 * 1024


def _ocr_enabled() -> bool:
    """是否启用 OCR（默认关闭，纯文本优先）。"""
    return os.getenv("ENABLE_OCR", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


def _is_image_ext(file_ext: str) -> bool:
    return file_ext.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}


def validate_file(file: UploadFile) -> Tuple[bool, str]:
    """
    验证文件类型和大小
    
    Returns:
        (is_valid, error_message)
    """
    if not file.filename:
        return False, "文件名不能为空"
    
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"不支持的文件类型: {file_ext}。支持的类型: {', '.join(ALLOWED_EXTENSIONS.keys())}"
    
    return True, ""


def generate_safe_filename(original_filename: str) -> str:
    """
    生成安全的文件名（添加时间戳和UUID避免冲突）
    
    Args:
        original_filename: 原始文件名
    
    Returns:
        安全的文件名
    """
    file_ext = Path(original_filename).suffix
    file_stem = Path(original_filename).stem
    
    # 清理文件名，移除特殊字符
    safe_stem = "".join(c for c in file_stem if c.isalnum() or c in (' ', '-', '_')).strip()
    
    # 生成唯一文件名：时间戳_UUID_原文件名.扩展名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{timestamp}_{unique_id}_{safe_stem}{file_ext}"


@router.post("/", response_model=FileUploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    auto_process: bool = True,
    use_ocr_preprocess: bool = True,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    文件上传API
    
    支持的文件格式：
    - 文档：PDF (.pdf), Word (.doc, .docx), PPT (.ppt, .pptx)
    - 图片：JPG, PNG, GIF, BMP, WEBP, TIFF
    
    文件将保存到 uploads 文件夹，并返回文件路径。
    
    Args:
        file: 上传的文件
    
    Returns:
        FileUploadResponse: 包含文件信息的响应
    """
    # 验证文件
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 确保上传目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # 生成安全的文件名
    safe_filename = generate_safe_filename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    file_ext = Path(file.filename).suffix.lower()
    file_type = file_ext[1:] if file_ext.startswith('.') else file_ext
    
    try:
        # 读取文件内容并检查大小
        file_content = await file.read()
        file_size = len(file_content)
        
        # 检查文件大小
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制（最大 {MAX_FILE_SIZE / 1024 / 1024:.0f}MB）"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="文件不能为空")
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="文件保存失败")
        
        # 保存到数据库
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (user_id, filename, file_path, file_type, file_size, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user.id, file.filename, file_path, file_type, file_size, 'uploaded'))
            document_id = cursor.lastrowid
            conn.commit()

        # 可选：上传后自动后台处理（解析/OCR -> 入知识库）
        # 纯文本模式下：图片不自动处理，避免触发 OCR 下载模型/耗时
        if auto_process and _is_image_ext(file_ext) and not _ocr_enabled():
            auto_process = False

        if auto_process:
            background_tasks.add_task(
                process_document_by_id,
                document_id=document_id,
                user_id=user.id,
                use_ocr_preprocess=use_ocr_preprocess,
            )
        
        # 返回绝对路径（相对于项目根目录）
        absolute_path = os.path.abspath(file_path)
        
        return FileUploadResponse(
            success=True,
            message="文件上传成功"
            + ("，已进入后台处理队列" if auto_process else "")
            + ("（当前为纯文本模式：图片已上传但未OCR/未入库）" if (_is_image_ext(file_ext) and not _ocr_enabled()) else ""),
            filename=file.filename,
            file_path=file_path,  # 返回相对路径，方便前端使用
            file_size=file_size,
            file_type=file_type
        )
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 如果保存失败，清理可能创建的文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"文件上传失败: {str(e)}"
        )


@router.post("/multiple", response_model=list[FileUploadResponse])
async def upload_multiple_files(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    批量文件上传API
    
    支持同时上传多个文件
    
    Args:
        files: 上传的文件列表
    
    Returns:
        List[FileUploadResponse]: 每个文件的上传结果列表
    """
    if not files:
        raise HTTPException(status_code=400, detail="请至少上传一个文件")
    
    results = []
    
    for file in files:
        try:
            result = await upload_file(
                background_tasks=background_tasks,
                file=file,
                auto_process=True,
                use_ocr_preprocess=True,
                user=user,
            )
            results.append(result)
        except HTTPException as e:
            # 如果单个文件上传失败，记录错误但继续处理其他文件
            results.append(FileUploadResponse(
                success=False,
                message=f"上传失败: {e.detail}",
                filename=file.filename or "未知文件",
                file_path="",
                file_size=0,
                file_type=""
            ))
    
    return results


@router.post("/by-path", response_model=FileUploadResponse)
async def upload_by_path(
    req: PathUploadRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    按“服务器本地路径”上传（像提交作业选择本地文件一样）。

    注意：该接口读取的是**后端服务器所在机器**的文件路径；
    如果你从浏览器在自己电脑选文件，应使用普通 multipart 上传（/api/upload/）。
    """
    src_path = os.path.expanduser(req.path)
    if not os.path.exists(src_path) or not os.path.isfile(src_path):
        raise HTTPException(status_code=404, detail="路径不存在或不是文件")

    original_name = os.path.basename(src_path)
    file_ext = Path(original_name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    safe_filename = generate_safe_filename(original_name)
    dst_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        shutil.copy2(src_path, dst_path)
        file_size = os.path.getsize(dst_path)
        file_type = file_ext[1:] if file_ext.startswith(".") else file_ext

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO documents (user_id, filename, file_path, file_type, file_size, status)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user.id, original_name, dst_path, file_type, file_size, "uploaded"),
            )
            document_id = cursor.lastrowid
            conn.commit()

        # 纯文本模式下：图片不自动处理，避免触发 OCR 下载模型/耗时
        if req.auto_process and _is_image_ext(file_ext) and not _ocr_enabled():
            req.auto_process = False

        if req.auto_process:
            background_tasks.add_task(
                process_document_by_id,
                document_id=document_id,
                user_id=user.id,
                use_ocr_preprocess=req.use_ocr_preprocess,
            )

        return FileUploadResponse(
            success=True,
            message="路径上传成功"
            + ("，已进入后台处理队列" if req.auto_process else "")
            + ("（当前为纯文本模式：图片已上传但未OCR/未入库）" if (_is_image_ext(file_ext) and not _ocr_enabled()) else ""),
            filename=original_name,
            file_path=dst_path,
            file_size=file_size,
            file_type=file_type,
        )
    except Exception as e:
        if os.path.exists(dst_path):
            try:
                os.remove(dst_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"路径上传失败: {str(e)}")

