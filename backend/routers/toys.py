"""
Toys Router — CRUD for toy characters
"""
import uuid
import base64
import os
import json
from fastapi import APIRouter, HTTPException
from models import ToyCreate, SuccessResponse
from database import get_db
from services.gemini_vision import extract_toy_features
from services.image_gen import generate_avatar
from prompts import get_character_system_prompt
from config import UPLOAD_DIR, AVATAR_DIR

router = APIRouter(prefix="/toys", tags=["Toys"])


@router.post("")
async def create_toy(toy: ToyCreate):
    """Create a new toy character from photo."""
    toy_id = str(uuid.uuid4())[:8]
    
    features = {}
    avatar_base64 = None
    photo_path = None
    avatar_path = None
    
    # 1. Save photo if provided
    if toy.photo_base64:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        photo_path = f"{UPLOAD_DIR}/{toy_id}_photo.jpg"
        with open(photo_path, "wb") as f:
            f.write(base64.b64decode(toy.photo_base64))
        
        # 2. Extract features from photo using Gemini Vision
        try:
            features = await extract_toy_features(toy.photo_base64)
        except Exception as e:
            print(f"Vision extraction failed: {e}")
            features = {
                "object_type": "장난감",
                "color": "여러 색",
                "features": "귀여운 장난감",
                "suggested_personality": "다정하고 호기심 많은 성격",
            }
        
        # 3. Generate avatar
        try:
            description = features.get("features", "귀여운 장난감")
            color = features.get("color", "여러 색")
            avatar_base64 = await generate_avatar(description, color)
            
            if avatar_base64:
                os.makedirs(AVATAR_DIR, exist_ok=True)
                avatar_path = f"{AVATAR_DIR}/{toy_id}_avatar.png"
                with open(avatar_path, "wb") as f:
                    f.write(base64.b64decode(avatar_base64))
        except Exception as e:
            print(f"Avatar generation failed: {e}")
    
    # 4. Build system prompt
    personality = features.get("suggested_personality", "다정하고 호기심 많은 성격")
    description = features.get("features", "")
    color = features.get("color", "")
    system_prompt = get_character_system_prompt(toy.name, personality, description, color)
    
    # 5. Save to DB
    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO toys (id, parent_id, name, photo_path, avatar_path, 
               description, personality, color, voice_name, system_prompt)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (toy_id, toy.parent_id, toy.name, photo_path, avatar_path,
             features.get("features"), personality, color,
             "Puck", system_prompt)
        )
        await db.commit()
    finally:
        await db.close()
    
    return {
        "success": True,
        "data": {
            "id": toy_id,
            "name": toy.name,
            "avatar_path": avatar_path,
            "avatar_base64": avatar_base64,
            "description": features.get("features"),
            "personality": personality,
            "color": color,
            "voice_name": "Puck",
        }
    }


@router.get("")
async def list_toys(parent_id: str = "parent-001"):
    """List all toys for a parent."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM toys WHERE parent_id = ? ORDER BY created_at DESC",
            (parent_id,)
        )
        rows = await cursor.fetchall()
        
        toys = []
        for row in rows:
            toy = dict(row)
            # Include avatar as base64 if file exists
            if toy.get("avatar_path") and os.path.exists(toy["avatar_path"]):
                with open(toy["avatar_path"], "rb") as f:
                    toy["avatar_base64"] = base64.b64encode(f.read()).decode("utf-8")
            else:
                toy["avatar_base64"] = None
            toys.append(toy)
        
        return {"success": True, "data": toys}
    finally:
        await db.close()


@router.get("/{toy_id}")
async def get_toy(toy_id: str):
    """Get a specific toy by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM toys WHERE id = ?", (toy_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "장난감을 찾을 수 없어요"})
        
        toy = dict(row)
        if toy.get("avatar_path") and os.path.exists(toy["avatar_path"]):
            with open(toy["avatar_path"], "rb") as f:
                toy["avatar_base64"] = base64.b64encode(f.read()).decode("utf-8")
        else:
            toy["avatar_base64"] = None
        
        return {"success": True, "data": toy}
    finally:
        await db.close()
