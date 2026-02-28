"""
Gemini Vision Service — Extract toy features from photo
"""
import json
import base64
from google import genai
from google.genai import types
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GEMINI_VISION_MODEL
from prompts import VISION_EXTRACTION_PROMPT


client = genai.Client(
    vertexai=True,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
)


async def extract_toy_features(photo_base64: str) -> dict:
    """
    Send toy photo to Gemini Vision and extract features.
    Returns dict with: object_type, color, features, suggested_personality, suggested_name
    """
    try:
        image_bytes = base64.b64decode(photo_base64)
        
        response = client.models.generate_content(
            model=GEMINI_VISION_MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(text=VISION_EXTRACTION_PROMPT),
                    ],
                )
            ],
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        
        result_text = response.text.strip()
        # Parse JSON from response
        features = json.loads(result_text)
        return features
        
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        return {
            "object_type": "장난감",
            "color": "알 수 없음",
            "features": "귀여운 장난감",
            "suggested_personality": "다정하고 호기심 많은 성격",
            "suggested_name": "친구"
        }
    except Exception as e:
        print(f"❌ Vision extraction error: {e}")
        return {
            "object_type": "장난감",
            "color": "알 수 없음", 
            "features": "귀여운 장난감",
            "suggested_personality": "다정하고 호기심 많은 성격",
            "suggested_name": "친구"
        }
