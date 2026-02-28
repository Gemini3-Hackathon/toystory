"""
Gemini Chat Service — Turn-based conversation with toy character
"""
from google import genai
from google.genai import types
from config import GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, GEMINI_CHAT_MODEL


client = genai.Client(
    vertexai=True,
    project=GOOGLE_CLOUD_PROJECT,
    location=GOOGLE_CLOUD_LOCATION,
)


async def chat_with_character(
    system_prompt: str,
    user_message: str,
    conversation_history: "list[dict] | None" = None
) -> str:
    """
    Send a message to Gemini and get a character response.
    
    Args:
        system_prompt: Character system prompt
        user_message: Child's message text
        conversation_history: Previous messages [{"role": "user"|"model", "text": "..."}]
    
    Returns:
        Character's reply text
    """
    try:
        # Build conversation contents
        contents = []
        
        # Add history if present
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                role = "user" if msg["role"] == "child" else "model"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["text"])]
                    )
                )
        
        # Add current user message
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            )
        )
        
        response = client.models.generate_content(
            model=GEMINI_CHAT_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.8,
                max_output_tokens=150,  # Keep responses short for kids
            ),
        )
        
        return response.text.strip()
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return "미안, 잠깐 말을 못 들었어! 다시 한번 말해줄래?"
