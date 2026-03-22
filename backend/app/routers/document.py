"""
文档管理路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.database import get_db_connection
from app.auth import CurrentUser, get_current_user_dep
from app.models import DocumentResponse, DocumentTextPreviewResponse
from app.services.knowledge_base import knowledge_base

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(user: CurrentUser = Depends(get_current_user_dep)):
    """获取所有文档列表"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, file_path, file_type, file_size, 
                   upload_time, status, page_count
            FROM documents
            WHERE user_id = ?
            ORDER BY upload_time DESC
        """, (user.id,))
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append(DocumentResponse(
                id=row['id'],
                filename=row['filename'],
                file_path=row['file_path'],
                file_type=row['file_type'],
                file_size=row['file_size'],
                upload_time=row['upload_time'],
                status=row['status'],
                page_count=row['page_count']
            ))
        
        return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, user: CurrentUser = Depends(get_current_user_dep)):
    """获取单个文档详情"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, filename, file_path, file_type, file_size,
                   upload_time, status, page_count
            FROM documents
            WHERE id = ? AND user_id = ?
        """, (document_id, user.id))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        return DocumentResponse(
            id=row['id'],
            filename=row['filename'],
            file_path=row['file_path'],
            file_type=row['file_type'],
            file_size=row['file_size'],
            upload_time=row['upload_time'],
            status=row['status'],
            page_count=row['page_count']
        )


@router.get("/{document_id}/text", response_model=DocumentTextPreviewResponse)
async def get_document_text(document_id: int, user: CurrentUser = Depends(get_current_user_dep)):
    """获取文档解析后的可复制文本（用于预览）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, filename, status, processed_text
            FROM documents
            WHERE id = ? AND user_id = ?
            """,
            (document_id, user.id),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")

        text = row["processed_text"] or ""
        if not text.strip():
            # 明确区分：未处理 vs 处理但无内容（如图片 OCR 关闭）
            if row["status"] != "completed":
                raise HTTPException(status_code=400, detail="文档尚未处理完成，暂无可预览文本")
            text = "（已完成处理，但未提取到可预览文本；若是图片文档且未启用OCR，则不会生成文本。）"

        return DocumentTextPreviewResponse(
            document_id=row["id"],
            status=row["status"],
            filename=row["filename"],
            text=text,
        )


@router.delete("/{document_id}")
async def delete_document(document_id: int, user: CurrentUser = Depends(get_current_user_dep)):
    """删除文档"""
    import os
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 获取文件路径
        cursor.execute("SELECT file_path FROM documents WHERE id = ? AND user_id = ?", (document_id, user.id))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="文档不存在")
        
        file_path = row['file_path']
        
        # 删除数据库记录
        cursor.execute("DELETE FROM documents WHERE id = ? AND user_id = ?", (document_id, user.id))
        cursor.execute("DELETE FROM document_chunks WHERE document_id = ? AND user_id = ?", (document_id, user.id))
        conn.commit()
        
        # 从知识库中删除（注意：FAISS不支持直接删除，这里只删除数据库记录）
        try:
            knowledge_base.delete_document(document_id, user.id)
        except Exception as e:
            print(f"从知识库删除文档失败: {e}")
        
        # 删除文件
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"删除文件失败: {e}")
        
        return {"message": "文档删除成功"}

