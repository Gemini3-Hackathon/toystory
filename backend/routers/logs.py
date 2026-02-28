"""
Logs Router — Conversation history and session logs for parents
"""
from fastapi import APIRouter, HTTPException
from database import get_db

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.get("/{toy_id}")
async def get_logs(toy_id: str):
    """Get conversation logs for a toy, grouped by session."""
    db = await get_db()
    try:
        # Verify toy exists
        cursor = await db.execute("SELECT name FROM toys WHERE id = ?", (toy_id,))
        toy = await cursor.fetchone()
        if not toy:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "장난감을 찾을 수 없어요"})
        
        # Get sessions with messages
        cursor = await db.execute(
            """SELECT s.*, t.name as toy_name 
               FROM sessions s JOIN toys t ON s.toy_id = t.id
               WHERE s.toy_id = ? 
               ORDER BY s.started_at DESC""",
            (toy_id,)
        )
        sessions = [dict(row) for row in await cursor.fetchall()]
        
        # Get messages for each session
        for session in sessions:
            cursor = await db.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session["id"],)
            )
            session["messages"] = [dict(row) for row in await cursor.fetchall()]
        
        return {
            "success": True,
            "data": {
                "toy_id": toy_id,
                "toy_name": dict(toy)["name"],
                "sessions": sessions
            }
        }
    finally:
        await db.close()
