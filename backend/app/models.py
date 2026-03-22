"""
数据模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: Optional[int] = None


class DocumentCreate(DocumentBase):
    file_path: str


class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    upload_time: datetime
    status: str
    page_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class DocumentTextPreviewResponse(BaseModel):
    document_id: int
    status: str
    filename: str
    text: str


class UploadResponse(BaseModel):
    message: str
    document_id: int
    filename: str


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    success: bool
    message: str
    filename: str
    file_path: str
    file_size: int
    file_type: str


class PathUploadRequest(BaseModel):
    """按路径上传请求（服务器本地路径）"""
    path: str
    auto_process: bool = True
    use_ocr_preprocess: bool = True


class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    document_ids: Optional[List[int]] = None


class SearchResult(BaseModel):
    document_id: int
    filename: str
    chunk_text: str
    score: float
    page_number: Optional[int] = None


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    document_ids: Optional[List[int]] = None
    # 聊天模式：'kb' 仅检索文档；'model' 仅用LLM直答；'hybrid' 二者结合
    mode: Optional[str] = "kb"


class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: Optional[List[SearchResult]] = None


class UserRegisterRequest(BaseModel):
    username: str
    password: str
    security_q1_season: str
    security_q2_birth_month: int
    security_q3_food: str


class UserLoginRequest(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    username: str
    security_q1_season: str
    security_q2_birth_month: int
    security_q3_food: str
    new_password: str


class AuthResponse(BaseModel):
    token: str
    username: str


class ChatSessionItem(BaseModel):
    session_id: str
    last_timestamp: datetime
    last_user_message: Optional[str] = None
    last_ai_response: Optional[str] = None

