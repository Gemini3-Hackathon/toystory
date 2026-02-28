"""
ToyTalk Backend — Toys 라우터
POST /toys (multipart), GET /toys, GET /toys/{id}, DELETE /toys/{id}
"""

import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from config.settings import settings
from db.database import get_db
from middleware.auth import get_current_user
from services.voice_matcher import match_voice

router = APIRouter(prefix="/toys", tags=["Toys"])


@router.post("", status_code=201)
async def create_toy(
    photo: UploadFile = File(...),
    toy_name: str = Form(...),
    child_name: str = Form(""),
    user_id: str = Depends(get_current_user),
):
    """장난감 등록 (사진 + 이름) → 아바타 생성"""
    db = await get_db()
    toy_id = str(uuid.uuid4())[:8]

    # 사진 저장
    os.makedirs(settings.PHOTOS_DIR, exist_ok=True)
    photo_path = os.path.join(settings.PHOTOS_DIR, f"{toy_id}_original.jpg")
    photo_bytes = await photo.read()
    with open(photo_path, "wb") as f:
        f.write(photo_bytes)

    # Stage 1: 장난감 분석
    try:
        from services.gemini_vision import analyze_toy

        analysis = await analyze_toy(photo_bytes)
    except Exception:
        analysis = {
            "type": "other",
            "primaryColor": "#808080",
            "secondaryColor": "#FFFFFF",
            "features": [],
            "expression": "neutral",
            "texture": "plush_fuzzy",
        }

    toy_type = analysis.get("type", "other")

    # Stage 2: Nano Banana 2 아바타 생성
    avatar_path = None
    try:
        from services.gemini_imagegen import generate_avatar, generate_avatar_from_photo, verify_avatar

        os.makedirs(settings.AVATARS_DIR, exist_ok=True)
        avatar_path = os.path.join(settings.AVATARS_DIR, f"{toy_id}.png")

        for attempt in range(3):
            try:
                # 먼저 원본 사진 기반 생성 시도 (더 정확한 유사도)
                avatar_bytes = await generate_avatar_from_photo(photo_bytes, analysis)
            except Exception:
                # 실패 시 텍스트 전용 생성
                avatar_bytes = await generate_avatar(analysis)

            # Stage 3: 품질 검증
            verification = await verify_avatar(analysis, avatar_bytes)
            if verification["passed"]:
                with open(avatar_path, "wb") as f:
                    f.write(avatar_bytes)
                break
        else:
            # 3회 실패 → 마지막 결과 저장 (검증 미통과라도)
            with open(avatar_path, "wb") as f:
                f.write(avatar_bytes)
    except Exception:
        avatar_path = photo_path

    # 음성 프로파일 매칭
    voice_profile = match_voice(toy_type)

    # DB INSERT
    now = datetime.now(timezone.utc).isoformat()
    await db.execute(
        """INSERT INTO toys (toy_id, owner_uid, toy_name, type, primary_color,
           secondary_color, features, expression, texture, voice_profile,
           child_name, avatar_path, original_photo_path, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            toy_id,
            user_id,
            toy_name,
            toy_type,
            analysis.get("primaryColor"),
            analysis.get("secondaryColor"),
            json.dumps(analysis.get("features", [])),
            analysis.get("expression"),
            analysis.get("texture"),
            json.dumps(voice_profile),
            child_name,
            avatar_path,
            photo_path,
            now,
        ),
    )
    await db.commit()

    return {
        "success": True,
        "data": {
            "toyId": toy_id,
            "toyName": toy_name,
            "type": toy_type,
            "avatarUrl": f"/uploads/avatars/{toy_id}.png",
            "voiceProfile": voice_profile,
            "createdAt": now,
        },
    }


@router.get("")
async def get_toys(user_id: str = Depends(get_current_user)):
    """내 장난감 목록"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT toy_id, toy_name, type, avatar_path, voice_profile,
           child_name, created_at FROM toys WHERE owner_uid = ?
           ORDER BY created_at DESC""",
        (user_id,),
    )
    rows = await cursor.fetchall()

    toys = []
    for row in rows:
        voice_profile = json.loads(row["voice_profile"]) if row["voice_profile"] else {}
        toys.append(
            {
                "toyId": row["toy_id"],
                "toyName": row["toy_name"],
                "type": row["type"],
                "avatarUrl": row["avatar_path"],
                "voiceProfile": voice_profile,
                "childName": row["child_name"],
                "createdAt": row["created_at"],
            }
        )

    return {"success": True, "data": toys}


@router.get("/{toy_id}")
async def get_toy(toy_id: str, user_id: str = Depends(get_current_user)):
    """장난감 상세"""
    db = await get_db()
    cursor = await db.execute(
        """SELECT * FROM toys WHERE toy_id = ? AND owner_uid = ?""",
        (toy_id, user_id),
    )
    row = await cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail={"code": "TOY_NOT_FOUND", "message": "장난감을 찾을 수 없습니다"},
        )

    voice_profile = json.loads(row["voice_profile"]) if row["voice_profile"] else {}
    features = json.loads(row["features"]) if row["features"] else []

    return {
        "success": True,
        "data": {
            "toyId": row["toy_id"],
            "toyName": row["toy_name"],
            "type": row["type"],
            "primaryColor": row["primary_color"],
            "secondaryColor": row["secondary_color"],
            "features": features,
            "expression": row["expression"],
            "texture": row["texture"],
            "voiceProfile": voice_profile,
            "childName": row["child_name"],
            "avatarUrl": row["avatar_path"],
            "createdAt": row["created_at"],
        },
    }


@router.delete("/{toy_id}")
async def delete_toy(toy_id: str, user_id: str = Depends(get_current_user)):
    """장난감 삭제 (CASCADE)"""
    db = await get_db()

    cursor = await db.execute(
        "SELECT toy_id FROM toys WHERE toy_id = ? AND owner_uid = ?",
        (toy_id, user_id),
    )
    if not await cursor.fetchone():
        raise HTTPException(
            status_code=404,
            detail={"code": "TOY_NOT_FOUND", "message": "장난감을 찾을 수 없습니다"},
        )

    await db.execute("DELETE FROM toys WHERE toy_id = ?", (toy_id,))
    await db.commit()

    return {"success": True, "data": {"deleted": toy_id}}
