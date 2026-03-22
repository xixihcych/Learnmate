"""
语义搜索路由
知识库向量搜索API
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List

from app.auth import CurrentUser, get_current_user_dep
from app.models import SearchQuery, SearchResult
from app.services.knowledge_base import knowledge_base

router = APIRouter()


@router.post("/", response_model=list[SearchResult])
async def semantic_search(query: SearchQuery, user: CurrentUser = Depends(get_current_user_dep)):
    """
    语义搜索API
    
    在知识库中搜索与查询相关的文档片段
    
    流程：
    1. 生成查询embedding
    2. 在FAISS中搜索最相似的文本块
    3. 返回结果
    
    Args:
        query: 搜索查询对象
            - query: 查询文本
            - top_k: 返回结果数量（默认5）
            - document_ids: 限制搜索的文档ID列表（可选）
    
    Returns:
        搜索结果列表，按相似度排序
    """
    try:
        if not query.query or not query.query.strip():
            raise HTTPException(status_code=400, detail="查询文本不能为空")
        
        # 执行知识库搜索
        results = knowledge_base.search(
            query=query.query,
            top_k=query.top_k,
            document_ids=query.document_ids,
            user_id=user.id,
        )
        
        # 转换为响应模型
        search_results = []
        for result in results:
            search_results.append(SearchResult(
                document_id=result['document_id'],
                filename=result['filename'],
                chunk_text=result['chunk_text'],
                score=result['score'],  # 距离分数（越小越相似）
                page_number=result.get('metadata', {}).get('page_number')
            ))
        
        return search_results
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/stats")
async def get_knowledge_base_stats(user: CurrentUser = Depends(get_current_user_dep)):
    """
    获取知识库统计信息
    
    Returns:
        知识库统计信息
    """
    try:
        stats = knowledge_base.get_stats(user_id=user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/rebuild")
async def rebuild_knowledge_base(
    only_completed: bool = Query(True, description="是否只重建 status=completed 的文档"),
    limit_docs: Optional[int] = Query(None, description="限制参与重建的文档数量（调试用）"),
    user: CurrentUser = Depends(get_current_user_dep),
):
    """从数据库 document_chunks 重建内存向量索引（服务重启后快速恢复用）。"""
    try:
        return knowledge_base.rebuild_from_db(
            only_completed=only_completed,
            limit_docs=limit_docs,
            user_id=user.id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")


@router.get("/document/{document_id}/stats")
async def get_document_stats(document_id: int, user: CurrentUser = Depends(get_current_user_dep)):
    """
    获取文档统计信息
    
    Args:
        document_id: 文档ID
    
    Returns:
        文档统计信息
    """
    try:
        stats = knowledge_base.get_document_stats(document_id, user.id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文档统计信息失败: {str(e)}")

