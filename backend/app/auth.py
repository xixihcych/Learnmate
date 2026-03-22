import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Header

from app.database import get_db_connection


@dataclass
class CurrentUser:
    id: int
    username: str


def _normalize_text(v: str) -> str:
    return (v or "").strip().lower()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    if "$" not in stored:
        return False
    salt, digest = stored.split("$", 1)
    check = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return hmac.compare_digest(check, digest)


def create_session_token(user_id: int, expires_hours: int = 24 * 30) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
            """,
            (user_id, token, expires_at.isoformat()),
        )
        conn.commit()
    return token


def get_user_by_token(token: str) -> Optional[CurrentUser]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT u.id, u.username, s.expires_at
            FROM user_sessions s
            JOIN users u ON u.id = s.user_id
            WHERE s.token = ?
            """,
            (token,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        expires_at = row["expires_at"]
        if expires_at:
            try:
                if datetime.fromisoformat(expires_at) < datetime.utcnow():
                    cursor.execute("DELETE FROM user_sessions WHERE token = ?", (token,))
                    conn.commit()
                    return None
            except Exception:
                pass
        return CurrentUser(id=row["id"], username=row["username"])


def get_current_user(authorization: Optional[str] = Header(default=None)) -> CurrentUser:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    token = authorization.split(" ", 1)[1].strip()
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    return user


def get_current_user_dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
