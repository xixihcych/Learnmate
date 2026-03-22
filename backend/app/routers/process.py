"""
文档处理路由
处理文档解析并添加到知识库
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import os

from app.database import get_db_connection
from app.auth import CurrentUser, get_current_user_dep
from app.services.document_processor import process_document_by_id

router = APIRouter()


def _ocr_enabled() -> bool:
    return os.getenv("ENABLE_OCR", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


@router.post("/document/{document_id}")
async def process_document(
    document_id: int,
    use_ocr_preprocess: bool = Query(True, description="当文件为图片时，是否启用OCR预处理（灰度/二值化/降噪）"),
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    处理文档：解析并添加到知识库
    
    流程：
    1. 从数据库获取文档信息
    2. 解析文档提取文本
    3. 文本切分
    4. 生成embedding
    5. 存入FAISS
    6. 更新数据库状态
    
    Args:
        document_id: 文档ID
    
    Returns:
        处理结果
    """
    try:
        # 纯文本模式下：阻止对图片文档进行处理（避免触发 OCR 下载模型/耗时）
        if not _ocr_enabled():
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM documents WHERE id = ? AND user_id = ?", (document_id, user.id))
                row = cursor.fetchone()
            if row:
                fp = (row["file_path"] or "").lower()
                if fp.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif")):
                    raise HTTPException(
                        status_code=400,
                        detail="当前为纯文本模式：图片不进行OCR处理。若需启用，请设置环境变量 ENABLE_OCR=true。",
                    )

        result = process_document_by_id(
            document_id=document_id,
            user_id=user.id,
            use_ocr_preprocess=use_ocr_preprocess,
        )
        # 保持旧响应字段兼容
        return {
            "success": True,
            "message": "文档处理成功",
            "document_id": document_id,
            "chunk_count": result.get("chunk_count", 0),
            "page_count": result.get("page_count", 0),
            "doc_type": result.get("doc_type"),
        }
    
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")






