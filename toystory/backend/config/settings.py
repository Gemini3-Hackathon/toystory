"""
ToyTalk Backend — 설정 모듈
환경변수 기반 설정 관리
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "toytalk.db")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "toytalk-hackathon-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24h
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://10.0.2.2:8000"
    ).split(",")

    # Vertex AI / Gemini
    GOOGLE_CLOUD_PROJECT: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    GOOGLE_CLOUD_LOCATION: str = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-northeast3")
    GEMINI_FLASH_MODEL: str = os.getenv("GEMINI_FLASH_MODEL", "gemini-2.0-flash")
    GEMINI_FLASH_EXP_MODEL: str = os.getenv("GEMINI_FLASH_EXP_MODEL", "gemini-3.1-flash-image-preview")  # Nano Banana 2
    GEMINI_LIVE_MODEL: str = os.getenv("GEMINI_LIVE_MODEL", "gemini-2.0-flash-live-001")

    # File paths
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    PHOTOS_DIR: str = os.path.join(UPLOAD_DIR, "photos")
    AVATARS_DIR: str = os.path.join(UPLOAD_DIR, "avatars")
    AUDIO_DIR: str = os.path.join(UPLOAD_DIR, "audio")

    # API
    API_PREFIX: str = "/api/v1"


settings = Settings()
