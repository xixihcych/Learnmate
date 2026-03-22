"""
数据库配置和初始化
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
import os

DATABASE_URL = "learnmate.db"


def get_db() -> Generator:
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_connection():
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """初始化数据库表"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # 用户表
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                security_q1_season TEXT NOT NULL,
                security_q2_birth_month INTEGER NOT NULL,
                security_q3_food TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # 登录会话表（本地简单 token 会话）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        
        # 文档表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processing',
                processed_text TEXT,
                page_count INTEGER,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 文档块表（用于向量化）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                user_id INTEGER,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                chunk_embedding BLOB,
                page_number INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # 聊天历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                document_ids TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 兼容旧库：补齐新增字段（SQLite 无 IF NOT EXISTS ADD COLUMN）
        def _ensure_column(table_name: str, column_name: str, ddl: str):
            cursor.execute(f"PRAGMA table_info({table_name})")
            cols = [r["name"] for r in cursor.fetchall()]
            if column_name not in cols:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {ddl}")

        _ensure_column("documents", "user_id", "user_id INTEGER")
        _ensure_column("document_chunks", "user_id", "user_id INTEGER")
        _ensure_column("chat_history", "user_id", "user_id INTEGER")
        
        conn.commit()
        print("数据库初始化完成")






