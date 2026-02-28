"""
Image Generation Service — Generate cartoon avatar from toy features
Uses Vertex AI Imagen
"""
import base64
from google import genai
from google.genai import types
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, IMAGEN_MODEL
from prompts import AVATAR_GENERATION_PROMPT_TEMPLATE


client = genai.Client(
    vertexai=True,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
)


from typing import Optional


async def generate_avatar(description: str, color: str) -> Optional[str]:
    """
    Generate a cartoon avatar image from toy description.
    
    Args:
        description: Toy features/description
        color: Main color of the toy
    
    Returns:
        Base64 encoded image string, or None if generation fails
    """
    try:
        prompt = AVATAR_GENERATION_PROMPT_TEMPLATE.format(
            description=description,
            color=color
        )
        
        response = client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                safety_filter_level="BLOCK_MEDIUM_AND_ABOVE",
            ),
        )
        
        if response.generated_images and len(response.generated_images) > 0:
            image = response.generated_images[0]
            image_bytes = image.image.image_bytes
            return base64.b64encode(image_bytes).decode("utf-8")
        
        return None
        
    except Exception as e:
        print(f"❌ Avatar generation error: {e}")
        return None
