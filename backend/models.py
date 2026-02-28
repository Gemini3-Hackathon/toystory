"""
Pydantic Models for ToyTalk API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Union, Any
from datetime import datetime


# --- Common Response ---

class ErrorDetail(BaseModel):
    code: str
    message: str


class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail


# --- Toy Models ---

class ToyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    photo_base64: Optional[str] = None
    parent_id: str = "parent-001"


class ToyResponse(BaseModel):
    id: str
    name: str
    photo_path: Optional[str] = None
    avatar_path: Optional[str] = None
    description: Optional[str] = None
    personality: Optional[str] = None
    color: Optional[str] = None
    voice_name: str = "Puck"
    system_prompt: Optional[str] = None
    created_at: str


# --- Talk Models ---

class TalkRequest(BaseModel):
    toy_id: str
    message: str
    session_id: Optional[str] = None


class TalkResponse(BaseModel):
    reply: str
    session_id: str
    audio_base64: Optional[str] = None


# --- TTS Models ---

class TTSRequest(BaseModel):
    text: str
    voice_name: str = "Puck"


class TTSResponse(BaseModel):
    audio_base64: str


# --- Session / Logs ---

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: str


class SessionResponse(BaseModel):
    id: str
    toy_id: str
    toy_name: Optional[str] = None
    started_at: str
    ended_at: Optional[str] = None
    duration_seconds: int = 0
    message_count: int = 0
    messages: Optional[List[MessageResponse]] = None


class SummaryResponse(BaseModel):
    toy_id: str
    toy_name: str
    total_sessions: int
    total_messages: int
    summary_text: str
