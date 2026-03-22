"""
知识图谱路由
提供知识图谱构建和可视化API
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse, HTMLResponse
from typing import Optional, List
import os
from pathlib import Path

from app.services.knowledge_graph import get_knowledge_graph
from app.services.knowledge_base import knowledge_base
from app.database import get_db_connection
from app.auth import CurrentUser, get_current_user_dep

router = APIRouter()

# 知识图谱可视化文件目录
KG_VIS_DIR = "knowledge_graphs"
os.makedirs(KG_VIS_DIR, exist_ok=True)


@router.post("/extract")
async def extract_from_text(
    text: str,
    source_id: Optional[int] = None,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    从文本中抽取实体和关系，添加到知识图谱
    
    Args:
        text: 输入文本
        source_id: 来源文档ID（可选）
    
    Returns:
        抽取结果统计
    """
    try:
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        kg = get_knowledge_graph(str(user.id))
        result = kg.process_text(text, source_id=source_id)
        
        return {
            "success": True,
            "message": "实体和关系抽取成功",
            **result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抽取失败: {str(e)}")


@router.post("/extract-from-document/{document_id}")
async def extract_from_document(
    document_id: int,
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    从文档中抽取实体和关系
    
    Args:
        document_id: 文档ID
    
    Returns:
        抽取结果
    """
    try:
        # 获取文档文本
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT processed_text, filename
                FROM documents
                WHERE id = ? AND status = 'completed' AND user_id = ?
            """, (document_id, user.id))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="文档不存在或未处理完成")
            
            text = row['processed_text']
            filename = row['filename']
        
        if not text:
            raise HTTPException(status_code=400, detail="文档文本为空")
        
        # 抽取实体和关系
        kg = get_knowledge_graph(str(user.id))
        result = kg.process_text(text, source_id=document_id)
        
        return {
            "success": True,
            "message": f"从文档 {filename} 抽取成功",
            "document_id": document_id,
            **result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"抽取失败: {str(e)}")


@router.post("/visualize")
async def generate_visualization(
    filename: Optional[str] = Query(None, description="输出文件名"),
    height: str = Query("800px", description="画布高度"),
    width: str = Query("100%", description="画布宽度"),
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    生成知识图谱可视化网页
    
    Args:
        filename: 输出文件名（可选，默认自动生成）
        height: 画布高度
        width: 画布宽度
    
    Returns:
        HTML文件路径
    """
    try:
        kg = get_knowledge_graph(str(user.id))
        
        # 检查是否有数据
        stats = kg.get_statistics()
        if stats["nodes_count"] == 0:
            raise HTTPException(status_code=400, detail="知识图谱为空，请先添加数据")
        
        # 生成文件名
        if not filename:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kg_u{user.id}_{timestamp}.html"
        
        if not filename.endswith('.html'):
            filename += '.html'
        
        output_path = os.path.join(KG_VIS_DIR, filename)
        
        # 生成可视化
        kg.visualize(output_path, height=height, width=width)
        
        return {
            "success": True,
            "message": "知识图谱可视化生成成功",
            "file_path": output_path,
            "url": f"/api/knowledge-graph/view/{filename}",
            "statistics": stats
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成可视化失败: {str(e)}")


@router.get("/view/{filename}")
async def view_visualization(filename: str):
    """
    查看知识图谱可视化
    
    Args:
        filename: HTML文件名
    
    Returns:
        HTML文件内容
    """
    file_path = os.path.join(KG_VIS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="可视化文件不存在")
    
    return FileResponse(file_path, media_type="text/html")


@router.get("/entity/{entity_name}")
async def get_entity_info(entity_name: str, user: CurrentUser = Depends(get_current_user_dep)):
    """
    获取实体的详细信息，包括相关笔记
    
    Args:
        entity_name: 实体名称
    
    Returns:
        实体信息
    """
    try:
        kg = get_knowledge_graph(str(user.id))
        info = kg.get_entity_info(entity_name)
        
        if "error" in info:
            raise HTTPException(status_code=404, detail=info["error"])
        
        return info
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体信息失败: {str(e)}")


@router.get("/statistics")
async def get_statistics(user: CurrentUser = Depends(get_current_user_dep)):
    """
    获取知识图谱统计信息
    
    Returns:
        统计信息
    """
    try:
        kg = get_knowledge_graph(str(user.id))
        stats = kg.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/triples")
async def get_triples(
    format: str = Query("json", description="导出格式: json 或 csv"),
    limit: Optional[int] = Query(None, description="限制返回数量"),
    user: CurrentUser = Depends(get_current_user_dep),
):
    """
    获取所有三元组
    
    Args:
        format: 导出格式
        limit: 限制返回数量
    
    Returns:
        三元组数据
    """
    try:
        kg = get_knowledge_graph(str(user.id))
        
        if format == "json":
            triples_data = [
                {
                    "entity1": t[0],
                    "relation": t[1],
                    "entity2": t[2]
                }
                for t in (kg.triples[:limit] if limit else kg.triples)
            ]
            return {
                "format": "json",
                "count": len(triples_data),
                "triples": triples_data
            }
        
        elif format == "csv":
            lines = ["entity1,relation,entity2"]
            triples = kg.triples[:limit] if limit else kg.triples
            for t in triples:
                lines.append(f'"{t[0]}","{t[1]}","{t[2]}"')
            return {
                "format": "csv",
                "count": len(triples),
                "data": "\n".join(lines)
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"不支持的格式: {format}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取三元组失败: {str(e)}")


@router.delete("/clear")
async def clear_knowledge_graph(user: CurrentUser = Depends(get_current_user_dep)):
    """
    清空知识图谱
    
    Returns:
        操作结果
    """
    try:
        kg = get_knowledge_graph(str(user.id))
        kg.graph.clear()
        kg.triples.clear()
        kg.entity_notes.clear()
        
        return {
            "success": True,
            "message": "知识图谱已清空"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空失败: {str(e)}")


@router.post("/build-from-documents")
async def build_from_all_documents(user: CurrentUser = Depends(get_current_user_dep)):
    """
    从所有已处理的文档构建知识图谱
    
    Returns:
        构建结果
    """
    try:
        # 获取所有已处理的文档
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, filename, processed_text
                FROM documents
                WHERE status = 'completed' AND processed_text IS NOT NULL AND user_id = ?
            """, (user.id,))
            rows = cursor.fetchall()
        
        if not rows:
            return {
                "success": False,
                "message": "没有已处理的文档",
                "processed_count": 0
            }
        
        kg = get_knowledge_graph(str(user.id))
        processed_count = 0
        total_triples = 0
        
        for row in rows:
            try:
                result = kg.process_text(row['processed_text'], source_id=row['id'])
                processed_count += 1
                total_triples += result['triples_count']
            except Exception as e:
                print(f"处理文档 {row['id']} 失败: {e}")
                continue
        
        return {
            "success": True,
            "message": f"从 {processed_count} 个文档构建知识图谱成功",
            "processed_count": processed_count,
            "total_triples": total_triples,
            "statistics": kg.get_statistics()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"构建失败: {str(e)}")






