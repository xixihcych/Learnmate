"""
文档/图片处理服务

将“读取文件 -> 文本提取（文档解析或OCR）-> 入知识库 -> 更新数据库状态”的流程集中到一处，
供 upload/process 路由复用。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.database import get_db_connection
from app.services.knowledge_base import knowledge_base
from app.utils.document_parser import parse_document

# OCR 默认关闭：纯文本优先（避免首次触发 EasyOCR 在线下载模型导致卡顿）
# 如需开启：export ENABLE_OCR=true
def _ocr_enabled() -> bool:
    return os.getenv("ENABLE_OCR", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}


def _extract_text(file_path: str, use_ocr_preprocess: bool = True) -> Tuple[str, int, str, Dict[str, Any]]:
    """
    根据文件类型提取文本。

    Returns:
        (text, page_count, doc_type, extra_metadata)
    """
    ext = Path(file_path).suffix.lower()
    if ext in IMAGE_EXTS:
        if not _ocr_enabled():
            # 纯文本模式：不对图片做 OCR，避免下载模型/耗时
            return "", 1, "image", {"ocr_skipped": True}

        # 仅在真正需要时才导入并调用 OCR（保持懒加载）
        from app.utils.ocr import extract_text_from_image_detailed, reset_ocr_processor  # local import

        # 与 /api/ocr/recognize 保持一致的兜底策略，避免“文档管理处理失败但AI问答OCR可用”
        ocr_errors = []
        ocr_result: Dict[str, Any]
        try:
            ocr_result = extract_text_from_image_detailed(file_path, use_preprocess=use_ocr_preprocess)
        except Exception as e1:
            ocr_errors.append(f"首次识别失败: {e1}")
            try:
                ocr_result = extract_text_from_image_detailed(file_path, use_preprocess=False)
            except Exception as e2:
                ocr_errors.append(f"关闭预处理重试失败: {e2}")
                try:
                    reset_ocr_processor()
                    ocr_result = extract_text_from_image_detailed(file_path, use_preprocess=False)
                except Exception as e3:
                    ocr_errors.append(f"重置OCR引擎后重试失败: {e3}")
                    # 图片 OCR 彻底失败时，不再让整条处理链失败：保留文档并标注错误信息。
                    return "", 1, "image", {
                        "ocr_failed": True,
                        "ocr_error": " | ".join(ocr_errors),
                        "ocr_confidence": 0.0,
                        "ocr_line_count": 0,
                    }

        text = ocr_result.get("text", "") or ""
        meta: Dict[str, Any] = {
            "ocr_confidence": ocr_result.get("confidence", 0.0),
            "ocr_line_count": ocr_result.get("line_count", 0),
        }
        # 图片按 1 “页”处理
        return text, 1, "image", meta

    # 其余走文档解析
    text, page_count, doc_type = parse_document(file_path)
    return text, page_count, doc_type, {}


def process_document_by_id(document_id: int, user_id: int, use_ocr_preprocess: bool = True) -> Dict[str, Any]:
    """
    按 document_id 处理并入库，失败会将 documents.status 置为 failed。
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, filename, file_path, file_type, status
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user_id),
        )
        row = cursor.fetchone()

    if not row:
        raise FileNotFoundError("文档不存在")

    file_path = row["file_path"]
    filename = row["filename"]

    if not os.path.exists(file_path):
        raise FileNotFoundError("文档文件不存在")

    try:
        text_content, page_count, doc_type, extra_meta = _extract_text(
            file_path=file_path, use_ocr_preprocess=use_ocr_preprocess
        )

        kb_error: Optional[str] = None
        try:
            chunk_count = knowledge_base.add_document(
                document_id=document_id,
                user_id=user_id,
                text=text_content,
                filename=filename,
                metadata={
                    "file_type": doc_type,
                    "page_count": page_count,
                    **extra_meta,
                },
            )
        except Exception as kb_e:
            # OCR/解析成功但向量入库失败（常见：离线环境模型下载失败）时，保留文本结果并标记警告
            chunk_count = 0
            kb_error = str(kb_e)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE documents
                SET processed_text = ?, page_count = ?, status = ?, metadata = ?
                WHERE id = ?
                """,
                (
                    text_content,
                    page_count,
                    "completed",
                    str({"doc_type": doc_type, "kb_error": kb_error, **extra_meta}),
                    document_id,
                ),
            )
            conn.commit()

        return {
            "success": True,
            "message": "处理成功" if not kb_error else "文本提取成功，但知识库入库失败",
            "document_id": document_id,
            "chunk_count": chunk_count,
            "page_count": page_count,
            "doc_type": doc_type,
            "kb_error": kb_error,
        }
    except Exception as e:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE documents SET status = ?, metadata = ? WHERE id = ?",
                ("failed", str({"error": str(e)}), document_id),
            )
            conn.commit()
        raise

