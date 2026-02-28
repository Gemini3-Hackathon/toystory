"""
ToyTalk Backend — 인증 라우터
POST /auth/signup, POST /auth/login
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from db.database import get_db
from middleware.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    nickname: str = Field(min_length=2, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup", status_code=201)
async def signup(req: SignupRequest):
    """회원가입"""
    db = await get_db()

    # 중복 이메일 확인
    cursor = await db.execute("SELECT user_id FROM users WHERE email = ?", (req.email,))
    existing = await cursor.fetchone()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={"code": "DUPLICATE_EMAIL", "message": "이미 가입된 이메일입니다"},
        )

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    password_hash = hash_password(req.password)

    await db.execute(
        "INSERT INTO users (user_id, email, password_hash, nickname, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, req.email, password_hash, req.nickname, now, now),
    )
    await db.commit()

    return {
        "success": True,
        "data": {
            "userId": user_id,
            "email": req.email,
            "nickname": req.nickname,
            "createdAt": now,
        },
    }


@router.post("/login")
async def login(req: LoginRequest):
    """로그인 → JWT 발급"""
    db = await get_db()

    cursor = await db.execute(
        "SELECT user_id, email, password_hash, nickname FROM users WHERE email = ?",
        (req.email,),
    )
    user = await cursor.fetchone()

    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 올바르지 않습니다"},
        )

    access_token = create_access_token(user["user_id"])
    refresh_token = create_refresh_token(user["user_id"])

    return {
        "success": True,
        "data": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {
                "userId": user["user_id"],
                "email": user["email"],
                "nickname": user["nickname"],
            },
        },
    }
