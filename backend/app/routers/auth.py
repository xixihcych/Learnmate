from fastapi import APIRouter, HTTPException

from app.auth import (
    _normalize_text,
    create_session_token,
    hash_password,
    verify_password,
)
from app.database import get_db_connection
from app.models import AuthResponse, PasswordResetRequest, UserLoginRequest, UserRegisterRequest

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register_user(payload: UserRegisterRequest):
    username = payload.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="用户名至少 3 位")
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    if not (1 <= int(payload.security_q2_birth_month) <= 12):
        raise HTTPException(status_code=400, detail="生日月份必须在 1-12")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        cursor.execute(
            """
            INSERT INTO users (
                username, password_hash, security_q1_season, security_q2_birth_month, security_q3_food
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                hash_password(payload.password),
                _normalize_text(payload.security_q1_season),
                int(payload.security_q2_birth_month),
                _normalize_text(payload.security_q3_food),
            ),
        )
        user_id = cursor.lastrowid
        conn.commit()

    token = create_session_token(user_id)
    return AuthResponse(token=token, username=username)


@router.post("/login", response_model=AuthResponse)
async def login_user(payload: UserLoginRequest):
    username = payload.username.strip()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="账号或密码错误")
    token = create_session_token(row["id"])
    return AuthResponse(token=token, username=username)


@router.post("/reset-password")
async def reset_password(payload: PasswordResetRequest):
    username = payload.username.strip()
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, security_q1_season, security_q2_birth_month, security_q3_food
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="用户不存在")

        ok = (
            _normalize_text(payload.security_q1_season) == (row["security_q1_season"] or "")
            and int(payload.security_q2_birth_month) == int(row["security_q2_birth_month"])
            and _normalize_text(payload.security_q3_food) == (row["security_q3_food"] or "")
        )
        if not ok:
            raise HTTPException(status_code=401, detail="安全问题答案不匹配")

        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hash_password(payload.new_password), row["id"]),
        )
        conn.commit()

    return {"success": True, "message": "密码重置成功，请重新登录"}
