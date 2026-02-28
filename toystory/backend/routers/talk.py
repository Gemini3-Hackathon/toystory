"""
ToyTalk Backend — Talk 라우터
POST /talk (턴제 대화: 텍스트 → Gemini → TTS → 응답)
"""

import json
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config.settings import settings
from db.database import get_db
from middleware.auth import get_current_user
from services.context_builder import build_context_window
from services.gemini_chat import chat_with_gemini

router = APIRouter(prefix="/talk", tags=["Talk"])


class TalkRequest(BaseModel):
    toyId: str
    text: str
    sessionId: str | None = None


@router.post("")
async def talk(req: TalkRequest, user_id: str = Depends(get_current_user)):
    """턴제 대화: 텍스트 → Gemini 응답 → (선택) TTS"""
    db = await get_db()

    # 장난감 확인
    cursor = await db.execute(
        "SELECT toy_name, type, voice_profile FROM toys WHERE toy_id = ? AND owner_uid = ?",
        (req.toyId, user_id),
    )
    toy = await cursor.fetchone()
    if not toy:
        raise HTTPException(
            status_code=404,
            detail={"code": "TOY_NOT_FOUND", "message": "장난감을 찾을 수 없습니다"},
        )

    # 세션 관리
    session_id = req.sessionId or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    cursor = await db.execute(
        "SELECT session_id FROM sessions WHERE session_id = ?", (session_id,)
    )
    if not await cursor.fetchone():
        await db.execute(
            "INSERT INTO sessions (session_id, toy_id, started_at) VALUES (?, ?, ?)",
            (session_id, req.toyId, now),
        )

    # ContextWindow 구축
    context_window = await build_context_window(req.toyId)

    # Gemini 대화
    reply = await chat_with_gemini(
        toy_name=toy["toy_name"],
        toy_type=toy["type"] or "default",
        user_text=req.text,
        context_window=context_window,
    )

    # 메시지 저장 (user + assistant)
    user_msg_id = str(uuid.uuid4())
    assistant_msg_id = str(uuid.uuid4())

    await db.execute(
        "INSERT INTO messages (message_id, session_id, toy_id, role, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (user_msg_id, session_id, req.toyId, "user", req.text, now),
    )
    await db.execute(
        "INSERT INTO messages (message_id, session_id, toy_id, role, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (assistant_msg_id, session_id, req.toyId, "assistant", reply, now),
    )

    # 세션 업데이트
    await db.execute(
        "UPDATE sessions SET last_message_at = ?, message_count = message_count + 2 WHERE session_id = ?",
        (now, session_id),
    )
    await db.commit()

    # TTS 생성 (선택)
    audio_url = None
    try:
        from services.gemini_tts import synthesize_speech

        voice_profile = json.loads(toy["voice_profile"]) if toy["voice_profile"] else {}
        audio_bytes = await synthesize_speech(reply, voice_profile)
        if audio_bytes:
            os.makedirs(settings.AUDIO_DIR, exist_ok=True)
            audio_filename = f"{assistant_msg_id}.wav"
            audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            audio_url = f"/uploads/audio/{audio_filename}"

            # 오디오 경로 업데이트
            await db.execute(
                "UPDATE messages SET audio_path = ? WHERE message_id = ?",
                (audio_path, assistant_msg_id),
            )
            await db.commit()
    except Exception:
        pass  # TTS 실패는 비차단

    return {
        "success": True,
        "data": {
            "sessionId": session_id,
            "message": {
                "messageId": assistant_msg_id,
                "role": "assistant",
                "text": reply,
                "audioUrl": audio_url,
                "createdAt": now,
            },
        },
    }
