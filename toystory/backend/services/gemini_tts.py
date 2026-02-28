"""
ToyTalk Backend — Gemini TTS 서비스
텍스트 → 음성 합성
"""

import logging

logger = logging.getLogger(__name__)


async def synthesize_speech(
    text: str,
    voice_profile: dict | None = None,
) -> bytes | None:
    """
    Gemini TTS 합성
    Returns: audio bytes (WAV/PCM) or None on failure
    """
    try:
        from google import genai
        from config.settings import settings

        client = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
        )

        tts_prompt = "밝고 친근한 목소리"
        if voice_profile and "ttsPrompt" in voice_profile:
            tts_prompt = voice_profile["ttsPrompt"]

        response = client.models.generate_content(
            model=settings.GEMINI_FLASH_MODEL,
            contents=f"Please say the following in Korean with a {tts_prompt} voice: {text}",
            config=genai.types.GenerateContentConfig(
                response_modalities=["AUDIO"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                return part.inline_data.data

        logger.warning("No audio data in TTS response")
        return None

    except Exception as e:
        logger.error(f"TTS synthesis failed: {e}")
        return None
