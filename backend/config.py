"""
ToyTalk Backend Configuration
"""
import os

# Google Cloud
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "aiden-lab-19644")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Gemini Models
GEMINI_VISION_MODEL = "gemini-2.0-flash"
GEMINI_CHAT_MODEL = "gemini-2.0-flash"
GEMINI_LIVE_MODEL = "gemini-live-2.5-flash-native-audio"

# ImageGen
IMAGEN_MODEL = "imagen-3.0-generate-002"

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "toytalk.db")

# File Storage
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
AVATAR_DIR = os.getenv("AVATAR_DIR", "avatars")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Gemini Live API
GEMINI_API_HOST = "us-central1-aiplatform.googleapis.com"
GEMINI_LIVE_SERVICE_URL = f"wss://{GEMINI_API_HOST}/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent"
