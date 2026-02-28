"""
ToyTalk Backend — TTS 라우터
POST /tts — 텍스트 → 음성 합성
"""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from db.database import get_db
from middleware.auth import get_current_user

router = APIRouter(prefix="/tts", tags=["TTS"])


class TTSRequest(BaseModel):
    text: str
    toyId: str | None = None


@router.post("")
async def text_to_speech(req: TTSRequest, user_id: str = Depends(get_current_user)):
    """텍스트 → TTS 합성 → 오디오 반환"""
    voice_profile = {}

    if req.toyId:
        db = await get_db()
        cursor = await db.execute(
            "SELECT voice_profile FROM toys WHERE toy_id = ? AND owner_uid = ?",
            (req.toyId, user_id),
        )
        toy = await cursor.fetchone()
        if toy and toy["voice_profile"]:
            voice_profile = json.loads(toy["voice_profile"])

    try:
        from services.gemini_tts import synthesize_speech

        audio_bytes = await synthesize_speech(req.text, voice_profile)
        if audio_bytes:
            return Response(
                content=audio_bytes,
                media_type="audio/wav",
                headers={"Content-Disposition": "attachment; filename=tts_output.wav"},
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={"code": "TTS_FAILED", "message": "음성 합성에 실패했습니다"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "TTS_FAILED", "message": f"음성 합성 오류: {str(e)}"},
        )
