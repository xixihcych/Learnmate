"""
知识库向量搜索系统
整合文本切分、embedding生成、FAISS存储和搜索功能

流程：
1. 文本切分
2. 生成embedding
3. 存入FAISS
4. 用户搜索返回最相似文本
"""
import os
import json
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import numpy as np

from app.utils.text_splitter import split_text_by_paragraph, split_text
from app.utils.vector_store import VectorStore, vector_store
from app.database import get_db_connection


class KnowledgeBase:
    """知识库管理类，整合向量搜索功能"""
    
    def __init__(self, vector_store: Optional[VectorStore] = None, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化知识库
        
        Args:
            vector_store: 向量存储实例，如果为None则使用全局实例
            chunk_size: 文本块大小（字符数）
            chunk_overlap: 文本块重叠大小
        """
        from app.utils.vector_store import vector_store as global_vector_store
        self.vector_store = vector_store if vector_store is not None else global_vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.index_path = "knowledge_base.index"
        self.metadata_path = "knowledge_base.metadata.json"
    
    def add_document(
        self,
        document_id: int,
        user_id: int,
        text: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        添加文档到知识库
        
        流程：
        1. 文本切分
        2. 生成embedding
        3. 存入FAISS
        
        Args:
            document_id: 文档ID
            text: 文档文本内容
            filename: 文件名
            metadata: 额外元数据
        
        Returns:
            添加的文本块数量
        """
        # 1. 文本切分
        chunks = self._split_document(text)
        
        if not chunks:
            return 0
        
        # 2. 准备元数据
        metadata_list = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                'document_id': document_id,
                'user_id': user_id,
                'chunk_index': i,
                'chunk_text': chunk,
                'filename': filename,
                'chunk_size': len(chunk),
            }
            
            # 添加额外元数据
            if metadata:
                chunk_metadata.update(metadata)
            
            metadata_list.append(chunk_metadata)
        
        # 3. 生成embedding并存入FAISS
        self.vector_store.add_documents(chunks, metadata_list)
        
        # 4. 保存到数据库（可选）
        self._save_chunks_to_db(document_id, user_id, chunks)
        
        return len(chunks)
    
    def _split_document(self, text: str) -> List[str]:
        """
        切分文档文本
        
        Args:
            text: 原始文本
        
        Returns:
            文本块列表
        """
        if not text or not text.strip():
            return []
        
        # 先按段落分割
        chunks = split_text_by_paragraph(text, max_chunk_size=self.chunk_size)
        
        # 如果段落太长，进一步分割
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                final_chunks.append(chunk)
            else:
                # 使用重叠分割
                sub_chunks = split_text(chunk, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                final_chunks.extend(sub_chunks)
        
        # 过滤空块
        final_chunks = [chunk.strip() for chunk in final_chunks if chunk.strip()]
        
        return final_chunks
    
    def _save_chunks_to_db(self, document_id: int, user_id: int, chunks: List[str]):
        """保存文本块到数据库"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                for i, chunk in enumerate(chunks):
                    cursor.execute("""
                        INSERT OR REPLACE INTO document_chunks 
                        (document_id, user_id, chunk_index, chunk_text)
                        VALUES (?, ?, ?, ?)
                    """, (document_id, user_id, i, chunk))
                conn.commit()
        except Exception as e:
            print(f"保存文本块到数据库失败: {e}")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
        user_id: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        流程：
        1. 生成查询embedding
        2. 在FAISS中搜索
        3. 返回最相似的文本
        
        Args:
            query: 查询文本
            top_k: 返回前k个结果
            document_ids: 限制搜索的文档ID列表（可选）
            min_score: 最小相似度分数（可选，距离越小越相似）
        
        Returns:
            搜索结果列表，每个结果包含：
            {
                'document_id': 文档ID,
                'filename': 文件名,
                'chunk_text': 文本块内容,
                'chunk_index': 块索引,
                'score': 相似度分数（距离，越小越相似）,
                'similarity': 相似度（0-1，越大越相似）
            }
        """
        if not query or not query.strip():
            return []
        
        # 执行向量搜索
        results = self.vector_store.search(query, top_k=top_k * 2)  # 多取一些以便过滤
        
        # 处理结果
        search_results = []
        for metadata, distance in results:
            doc_id = metadata.get('document_id')
            
            # 过滤文档ID
            if document_ids and doc_id not in document_ids:
                continue
            if user_id is not None and metadata.get("user_id") != user_id:
                continue
            
            # 计算相似度（将距离转换为相似度，0-1范围）
            # L2距离越小，相似度越高
            # 使用简单的转换：similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + distance)
            
            # 过滤最小相似度
            if min_score is not None and similarity < min_score:
                continue
            
            result = {
                'document_id': doc_id,
                'filename': metadata.get('filename', '未知'),
                'chunk_text': metadata.get('chunk_text', ''),
                'chunk_index': metadata.get('chunk_index', 0),
                'score': float(distance),
                'similarity': float(similarity),
                'metadata': {k: v for k, v in metadata.items() if k not in ['chunk_text']}
            }
            
            search_results.append(result)
            
            # 达到top_k就停止
            if len(search_results) >= top_k:
                break
        
        return search_results
    
    def delete_document(self, document_id: int, user_id: int):
        """
        从知识库中删除文档
        
        注意：FAISS不支持直接删除，这里只从数据库删除记录
        实际应用中可能需要重建索引
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM document_chunks WHERE document_id = ? AND user_id = ?", (document_id, user_id))
                conn.commit()
        except Exception as e:
            print(f"删除文档块失败: {e}")
    
    def get_document_stats(self, document_id: int, user_id: int) -> Dict[str, Any]:
        """获取文档统计信息"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as chunk_count,
                           AVG(LENGTH(chunk_text)) as avg_chunk_size
                    FROM document_chunks
                    WHERE document_id = ? AND user_id = ?
                """, (document_id, user_id))
                row = cursor.fetchone()
                
                return {
                    'document_id': document_id,
                    'chunk_count': row['chunk_count'] if row else 0,
                    'avg_chunk_size': row['avg_chunk_size'] if row else 0
                }
        except Exception as e:
            return {
                'document_id': document_id,
                'error': str(e)
            }
    
    def save_index(self, filepath: Optional[str] = None):
        """保存向量索引"""
        path = filepath or self.index_path
        self.vector_store.save(path)
    
    def load_index(self, filepath: Optional[str] = None):
        """加载向量索引"""
        path = filepath or self.index_path
        self.vector_store.load(path)
    
    def get_stats(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            total_chunks = 0
            
            # 统计文档数量
            document_ids = set()
            if self.vector_store.metadata:
                for meta in self.vector_store.metadata:
                    if user_id is not None and meta.get("user_id") != user_id:
                        continue
                    total_chunks += 1
                    doc_id = meta.get('document_id')
                    if doc_id:
                        document_ids.add(doc_id)

            return {
                'total_chunks': total_chunks,
                'total_documents': len(document_ids),
                'index_dimension': self.vector_store.dimension if self.vector_store.index else None,
                'index_size': self.vector_store.index.ntotal if self.vector_store.index else 0
            }
        except Exception as e:
            return {'error': str(e)}

    def rebuild_from_db(
        self,
        only_completed: bool = True,
        limit_docs: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        从 SQLite 的 document_chunks 表重建内存向量索引。

        说明：
        - 当前向量索引默认常驻内存，服务重启后会丢失；
          该方法用于快速恢复（让搜索/问答立刻可用）。
        - 仅重建，不会修改 documents.status。
        """
        try:
            # 清空现有索引
            self.vector_store.index = None
            self.vector_store.metadata = []

            with get_db_connection() as conn:
                cursor = conn.cursor()

                where_parts: List[str] = []
                if only_completed:
                    where_parts.append("d.status = 'completed'")
                if user_id is not None:
                    where_parts.append("d.user_id = ?")

                where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

                limit = f"LIMIT {int(limit_docs)}" if limit_docs else ""

                params: List[Any] = []
                if user_id is not None:
                    params.append(user_id)

                cursor.execute(
                    f"""
                    SELECT d.id as document_id, d.user_id as user_id, d.filename as filename, c.chunk_index as chunk_index, c.chunk_text as chunk_text
                    FROM document_chunks c
                    JOIN documents d ON d.id = c.document_id
                    {where}
                    ORDER BY d.id ASC, c.chunk_index ASC
                    {limit}
                    """
                    ,
                    tuple(params),
                )
                rows = cursor.fetchall()

            if not rows:
                return {"success": True, "message": "数据库中没有可重建的 chunks", **self.get_stats(user_id=user_id)}

            texts: List[str] = []
            metas: List[Dict[str, Any]] = []
            doc_ids = set()

            for r in rows:
                doc_id = int(r["document_id"])
                doc_ids.add(doc_id)
                txt = r["chunk_text"] or ""
                if not txt.strip():
                    continue
                texts.append(txt)
                metas.append(
                    {
                        "document_id": doc_id,
                        "user_id": int(r["user_id"]) if r["user_id"] is not None else None,
                        "chunk_index": int(r["chunk_index"] or 0),
                        "chunk_text": txt,
                        "filename": r["filename"] or "未知",
                    }
                )

            if not texts:
                return {"success": True, "message": "chunks 为空，无法重建", **self.get_stats(user_id=user_id)}

            self.vector_store.add_documents(texts, metas)

            return {
                "success": True,
                "message": "重建完成",
                "rebuilt_documents": len(doc_ids),
                "rebuilt_chunks": len(texts),
                **self.get_stats(user_id=user_id),
            }
        except Exception as e:
            return {"success": False, "message": f"重建失败: {e}", **self.get_stats(user_id=user_id)}


# 全局知识库实例
knowledge_base = KnowledgeBase()

