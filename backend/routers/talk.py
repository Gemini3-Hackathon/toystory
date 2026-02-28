"""
Talk Router — Turn-based text conversation with toy characters
"""
import uuid
from fastapi import APIRouter, HTTPException
from models import TalkRequest
from database import get_db
from services.gemini_chat import chat_with_character

router = APIRouter(prefix="/talk", tags=["Talk"])


@router.post("")
async def talk(request: TalkRequest):
    """Send a message to a toy character and get a response."""
    
    db = await get_db()
    try:
        # Get toy info
        cursor = await db.execute("SELECT * FROM toys WHERE id = ?", (request.toy_id,))
        toy = await cursor.fetchone()
        
        if not toy:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "장난감을 찾을 수 없어요"})
        
        toy = dict(toy)
        system_prompt = toy.get("system_prompt", "")
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = str(uuid.uuid4())[:8]
            await db.execute(
                "INSERT INTO sessions (id, toy_id) VALUES (?, ?)",
                (session_id, request.toy_id)
            )
        
        # Get conversation history
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        )
        history_rows = await cursor.fetchall()
        history = [{"role": r["role"], "text": r["content"]} for r in history_rows]
        
        # Get AI response
        reply = await chat_with_character(system_prompt, request.message, history)
        
        # Save messages
        child_msg_id = str(uuid.uuid4())[:8]
        char_msg_id = str(uuid.uuid4())[:8]
        
        await db.execute(
            "INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, 'child', ?)",
            (child_msg_id, session_id, request.message)
        )
        await db.execute(
            "INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, 'character', ?)",
            (char_msg_id, session_id, reply)
        )
        
        # Update session message count
        await db.execute(
            """UPDATE sessions SET message_count = (
                SELECT COUNT(*) FROM messages WHERE session_id = ?
            ) WHERE id = ?""",
            (session_id, session_id)
        )
        
        await db.commit()
        
        return {
            "success": True,
            "data": {
                "reply": reply,
                "session_id": session_id,
            }
        }
    finally:
        await db.close()
