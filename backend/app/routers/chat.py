"""
AI问答路由（RAG）
实现检索增强生成问答系统

流程：
1. 用户输入问题
2. 在FAISS中检索相关文本
3. 将文本作为上下文
4. 调用 Gemini API 生成回答
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import uuid
from typing import Optional, List
import json

from app.models import ChatMessage, ChatResponse, SearchResult, ChatSessionItem
from app.services.knowledge_base import knowledge_base
from app.database import get_db_connection
from app.auth import CurrentUser, get_current_user_dep

import os
import re


def _use_deepseek() -> bool:
    """是否使用 DeepSeek（默认 false -> Gemini）。"""
    return os.getenv("USE_DEEPSEEK", "false").strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_llm_service():
    """
    按环境变量选择 LLM 服务。
    说明：不要在模块 import 时就固定选择，避免 .env/环境变量在启动后未生效导致一直走 Gemini。
    """
    if _use_deepseek():
        from app.services.deepseek_service import get_deepseek_service

        return get_deepseek_service()
    else:
        from app.services.gemini_service import get_gemini_service

        return get_gemini_service()

router = APIRouter()


def _search_kb_context(
    user_query: str,
    document_ids: Optional[List[int]],
    user_id: int,
) -> tuple[List[SearchResult], Optional[str]]:
    """
    搜索知识库并返回可读错误信息（避免把依赖缺失误报成“无相关信息”）。
    """
    try:
        search_results = knowledge_base.search(
            query=user_query,
            top_k=5,
            document_ids=document_ids,
            user_id=user_id,
        )
        context_results: List[SearchResult] = []
        for result in search_results:
            context_results.append(SearchResult(
                document_id=result['document_id'],
                filename=result['filename'],
                chunk_text=result['chunk_text'],
                score=result['score'],
                page_number=result.get('metadata', {}).get('page_number')
            ))
        return context_results, None
    except Exception as e:
        err = str(e)
        if "sentence-transformers" in err.lower() or "torch" in err.lower():
            return [], "知识库检索不可用：缺少 embedding 依赖（sentence-transformers/torch）。请先安装并重建索引。"
        return [], f"知识库检索失败：{err}"


def _is_small_talk(query: str) -> bool:
    """识别简短寒暄/闲聊，hybrid 模式下优先走模型直答。"""
    q = (query or "").strip().lower()
    if not q:
        return False
    if len(q) <= 8 and q in {"hi", "hello", "hey", "你好", "您好", "在吗", "嗨"}:
        return True
    return bool(re.fullmatch(r"[你好您好哈喽嗨在吗\?\!，。,. ]{1,12}", q))


def generate_ai_response(query: str, context: List[SearchResult], strict_context: bool = True) -> str:
    """
    基于检索到的上下文生成AI回答
    
    RAG流程：
    1. 从知识库检索相关文本（已完成）
    2. 构建上下文
    3. 调用LLM API生成回答（DeepSeek/Gemini）
    
    Args:
        query: 用户问题
        context: 检索到的上下文结果列表
    
    Returns:
        AI生成的回答
    """
    # 提取上下文文本（使用前5个最相关的结果）
    context_texts = [result.chunk_text for result in context[:5]]
    try:
        llm_service = _get_llm_service()
        system_prompt = None
        if not strict_context:
            # hybrid 模式：允许先正常回答，再结合上下文补充；避免把“你好”误判为无法回答。
            system_prompt = (
                "你是一个中文智能助手。请优先回答用户问题本身。"
                "如果给定上下文与问题相关，请整合上下文并可简要引用；"
                "如果上下文无关或噪声较大，不要被其限制，可直接给出通用回答。"
            )
        response = llm_service.generate_response(
            query=query,
            context=context_texts,
            system_prompt=system_prompt,
            temperature=0.7
        )
        return response
    except Exception as e:
        # 如果LLM API调用失败，返回降级回答
        error_msg = str(e)
        api_key_name = "DEEPSEEK_API_KEY" if _use_deepseek() else "GEMINI_API_KEY"
        if "API密钥" in error_msg or "api_key" in error_msg.lower():
            return f"LLM API配置错误：{error_msg}。请检查{api_key_name}环境变量。"
        else:
            # 返回基于上下文的简化摘要
            context_summary = "\n\n".join([
                f"[来源: {result.filename}]\n{result.chunk_text[:200]}..."
                for result in context[:3]
            ]) if context else "（当前无文档上下文）"
            llm_name = "DeepSeek" if _use_deepseek() else "Gemini"
            return f"（注意：{llm_name} API调用失败，这是基于检索结果的简化回答）\n\n{context_summary}"


def generate_model_only_response(query: str) -> str:
    """仅用LLM直答，不附带文档上下文。"""
    try:
        llm_service = _get_llm_service()
        system_prompt = (
            "你是一个中文智能助手。当前没有可用文档上下文时，"
            "请直接根据常识与通用知识回答用户问题；"
            "若问题涉及特定文档事实且你无法确认，请明确说明需要相关文档上下文。"
        )
        return llm_service.generate_response(
            query=query,
            context=[],
            system_prompt=system_prompt,
            temperature=0.7
        )
    except Exception as e:
        error_msg = str(e)
        api_key_name = "DEEPSEEK_API_KEY" if _use_deepseek() else "GEMINI_API_KEY"
        if "API密钥" in error_msg or "api_key" in error_msg.lower():
            return f"LLM API配置错误：{error_msg}。请检查{api_key_name}环境变量。"
        return f"LLM 直答失败：{error_msg}"


@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage, user: CurrentUser = Depends(get_current_user_dep)):
    """
    AI问答接口（RAG）
    
    完整的RAG流程：
    1. 用户输入问题
    2. 在FAISS中检索相关文本
    3. 将文本作为上下文
    4. 调用 Gemini API 生成回答
    
    Args:
        message: 聊天消息对象
            - message: 用户问题
            - session_id: 会话ID（可选）
            - document_ids: 限制搜索的文档ID列表（可选）
    
    Returns:
        ChatResponse: 包含AI回答和来源信息
    """
    try:
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        # 生成或使用session_id
        session_id = message.session_id or str(uuid.uuid4())
        
        mode = (message.mode or "kb").strip().lower()
        if mode not in {"kb", "hybrid"}:
            mode = "kb"
        context_results: List[SearchResult] = []
        kb_error: Optional[str] = None

        if mode in {"kb", "hybrid"}:
            context_results, kb_error = _search_kb_context(message.message, message.document_ids, user.id)

        if mode == "kb":
            if kb_error:
                ai_response = kb_error
            elif not context_results:
                ai_response = "抱歉，我在知识库中没有找到相关信息。请尝试重新表述您的问题，或者上传相关文档到知识库。"
            else:
                ai_response = generate_ai_response(
                    query=message.message,
                    context=context_results
                )
            sources_to_return = context_results[:3]
        else:  # hybrid
            # hybrid：闲聊优先直答；知识问题再融合上下文
            if _is_small_talk(message.message):
                ai_response = generate_model_only_response(message.message)
            else:
                ai_response = generate_ai_response(
                    query=message.message,
                    context=context_results,
                    strict_context=False,
                ) if context_results else generate_model_only_response(message.message)
            sources_to_return = context_results[:3]
        
        # 保存聊天历史
        doc_ids_str = ','.join(map(str, message.document_ids)) if message.document_ids else None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_id, session_id, user_message, ai_response, document_ids)
                VALUES (?, ?, ?, ?, ?)
            """, (user.id, session_id, message.message, ai_response, doc_ids_str))
            conn.commit()
        
        return ChatResponse(response=ai_response, session_id=session_id, sources=sources_to_return)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@router.post("/stream")
async def chat_stream(message: ChatMessage, user: CurrentUser = Depends(get_current_user_dep)):
    """
    流式AI问答接口（RAG）
    
    返回流式响应，实时显示生成过程
    """
    try:
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="问题不能为空")
        
        session_id = message.session_id or str(uuid.uuid4())
        
        mode = (message.mode or "kb").strip().lower()
        if mode not in {"kb", "hybrid"}:
            mode = "kb"
        context_results: List[SearchResult] = []
        kb_error: Optional[str] = None
        if mode in {"kb", "hybrid"}:
            context_results, kb_error = _search_kb_context(message.message, message.document_ids, user.id)
        context_texts = [r.chunk_text for r in context_results[:5]]
        
        # 流式生成回答
        def generate():
            try:
                full_response = ""
                if mode == "kb" and kb_error:
                    full_response = kb_error
                    yield f"data: {json.dumps({'chunk': kb_error, 'done': False}, ensure_ascii=False)}\n\n"
                else:
                    llm_service = _get_llm_service()
                    gen_iter = llm_service.generate_stream_response(
                        query=message.message,
                        context=context_texts if mode in {"kb", "hybrid"} else []
                    )
                    for chunk in gen_iter:
                        full_response += chunk
                        yield f"data: {json.dumps({'chunk': chunk, 'done': False}, ensure_ascii=False)}\n\n"
                
                # 发送完成信号
                yield f"data: {json.dumps({'chunk': '', 'done': True, 'full_response': full_response}, ensure_ascii=False)}\n\n"
                
                # 保存聊天历史
                doc_ids_str = ','.join(map(str, message.document_ids)) if message.document_ids else None
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO chat_history (user_id, session_id, user_message, ai_response, document_ids)
                        VALUES (?, ?, ?, ?, ?)
                    """, (user.id, session_id, message.message, full_response, doc_ids_str))
                    conn.commit()
            
            except Exception as e:
                error_msg = str(e)
                yield f"data: {json.dumps({'error': error_msg}, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式问答失败: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, user: CurrentUser = Depends(get_current_user_dep)):
    """获取聊天历史"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_message, ai_response, timestamp
            FROM chat_history
            WHERE session_id = ? AND user_id = ?
            ORDER BY timestamp ASC
        """, (session_id, user.id))
        rows = cursor.fetchall()
        
        history = [
            {
                "user": row['user_message'],
                "ai": row['ai_response'],
                "timestamp": row['timestamp']
            }
            for row in rows
        ]
        
        return {"session_id": session_id, "history": history}


@router.get("/sessions", response_model=list[ChatSessionItem])
async def list_chat_sessions(user: CurrentUser = Depends(get_current_user_dep)):
    """列出当前用户的会话（按最近消息时间倒序）"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
              session_id,
              MAX(timestamp) AS last_timestamp,
              (SELECT user_message FROM chat_history h2
                 WHERE h2.user_id = h.user_id AND h2.session_id = h.session_id
                 ORDER BY h2.timestamp DESC, h2.id DESC
                 LIMIT 1) AS last_user_message,
              (SELECT ai_response FROM chat_history h2
                 WHERE h2.user_id = h.user_id AND h2.session_id = h.session_id
                 ORDER BY h2.timestamp DESC, h2.id DESC
                 LIMIT 1) AS last_ai_response
            FROM chat_history h
            WHERE user_id = ?
            GROUP BY session_id
            ORDER BY last_timestamp DESC
            LIMIT 100
            """,
            (user.id,),
        )
        rows = cursor.fetchall()
    return [
        ChatSessionItem(
            session_id=r["session_id"],
            last_timestamp=r["last_timestamp"],
            last_user_message=r["last_user_message"],
            last_ai_response=r["last_ai_response"],
        )
        for r in rows
    ]

