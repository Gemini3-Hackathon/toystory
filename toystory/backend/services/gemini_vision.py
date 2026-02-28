"""
ToyTalk Backend — Gemini Vision 서비스
Stage 1: 장난감 사진 분석 → JSON 추출
"""

import json
import logging

logger = logging.getLogger(__name__)


async def analyze_toy(image_bytes: bytes) -> dict:
    """
    Gemini Vision으로 장난감 사진 분석 → JSON 추출
    Returns: {"type", "primaryColor", "secondaryColor", "features", "expression", "texture"}
    """
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
            contents=[
                genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                'Analyze this toy photo. Return ONLY valid JSON with these fields: '
                '{"type": "bear|dinosaur|doll|cat|dog|truck|robot|dragon|other", '
                '"primaryColor": "#hex", "secondaryColor": "#hex", '
                '"features": ["feature1", "feature2"], '
                '"expression": "smiling|neutral|excited|sad", '
                '"texture": "plush_fuzzy|plastic_smooth|wood|fabric|rubber"}',
            ],
        )

        # JSON 추출
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)

    except Exception as e:
        logger.error(f"Toy analysis failed: {e}")
        # 기본값 반환
        return {
            "type": "other",
            "primaryColor": "#808080",
            "secondaryColor": "#FFFFFF",
            "features": [],
            "expression": "neutral",
            "texture": "plush_fuzzy",
        }
