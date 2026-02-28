"""
ToyTalk Backend — Gemini Chat 서비스
턴제 대화 — Gemini LLM 호출
"""

import logging

from config.prompts import build_system_instruction
from middleware.safety import check_safety, SAFE_FALLBACK

logger = logging.getLogger(__name__)


async def chat_with_gemini(
    toy_name: str,
    toy_type: str,
    user_text: str,
    context_window: str = "",
) -> str:
    """
    턴제 대화: 사용자 텍스트 → Gemini → 응답 텍스트
    """
    # Layer 2 안전 필터 (입력)
    safety_check = check_safety(user_text)
    if not safety_check["safe"]:
        logger.warning(f"Safety filter blocked input: {safety_check['reason']}")
        return SAFE_FALLBACK

    system_instruction = build_system_instruction(
        toy_name=toy_name,
        toy_type=toy_type,
        context_window=context_window,
    )

    try:
        from google import genai
        from config.settings import settings

        client = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
        )

        response = client.models.generate_content(
            model=settings.GEMINI_FLASH_MODEL,
            contents=user_text,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,
                max_output_tokens=200,
            ),
        )

        reply = response.text.strip()

        # Layer 2 안전 필터 (출력)
        output_check = check_safety(reply)
        if not output_check["safe"]:
            logger.warning(f"Safety filter blocked output: {output_check['reason']}")
            return SAFE_FALLBACK

        return reply

    except Exception as e:
        logger.error(f"Gemini chat failed: {e}")
        return "음... 잘 못 들었어! 다시 말해줄래?"
