"""
TTS Router — Text-to-Speech using Gemini
"""
from fastapi import APIRouter
from models import TTSRequest

router = APIRouter(prefix="/tts", tags=["TTS"])


@router.post("")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech audio.
    Note: In the Live API flow, TTS is handled natively.
    This endpoint is for turn-based fallback mode.
    """
    # For MVP, TTS is handled by the Live API's native audio output.
    # This endpoint serves as a placeholder for turn-based mode.
    return {
        "success": True,
        "data": {
            "text": request.text,
            "voice_name": request.voice_name,
            "message": "TTS는 Live API의 네이티브 오디오 출력으로 처리됩니다."
        }
    }
