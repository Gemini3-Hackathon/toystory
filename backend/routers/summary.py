"""
Summary Router — AI-generated conversation summaries for parents
"""
from fastapi import APIRouter, HTTPException
from database import get_db
from services.gemini_chat import chat_with_character
from prompts import SUMMARY_PROMPT_TEMPLATE

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/{toy_id}")
async def get_summary(toy_id: str):
    """Generate an AI summary of recent conversations for a toy."""
    db = await get_db()
    try:
        # Get toy info
        cursor = await db.execute("SELECT name FROM toys WHERE id = ?", (toy_id,))
        toy = await cursor.fetchone()
        if not toy:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "장난감을 찾을 수 없어요"})
        
        toy_name = dict(toy)["name"]
        
        # Get recent messages
        cursor = await db.execute(
            """SELECT m.role, m.content, m.created_at 
               FROM messages m 
               JOIN sessions s ON m.session_id = s.id 
               WHERE s.toy_id = ? 
               ORDER BY m.created_at DESC 
               LIMIT 50""",
            (toy_id,)
        )
        messages = [dict(row) for row in await cursor.fetchall()]
        
        if not messages:
            return {
                "success": True,
                "data": {
                    "toy_id": toy_id,
                    "toy_name": toy_name,
                    "total_sessions": 0,
                    "total_messages": 0,
                    "summary_text": "아직 대화 기록이 없어요."
                }
            }
        
        # Build conversation text
        conversation_text = "\n".join([
            f"{'아이' if m['role'] == 'child' else toy_name}: {m['content']}"
            for m in reversed(messages)
        ])
        
        # Generate summary using Gemini
        prompt = SUMMARY_PROMPT_TEMPLATE.format(
            toy_name=toy_name,
            conversation_text=conversation_text
        )
        
        summary = await chat_with_character(
            system_prompt="당신은 어린이 교육 전문가입니다. 부모님에게 아이의 대화 내용을 분석해 요약해주세요.",
            user_message=prompt
        )
        
        # Get stats
        cursor = await db.execute(
            "SELECT COUNT(*) FROM sessions WHERE toy_id = ?", (toy_id,)
        )
        total_sessions = (await cursor.fetchone())[0]
        
        cursor = await db.execute(
            """SELECT COUNT(*) FROM messages m 
               JOIN sessions s ON m.session_id = s.id 
               WHERE s.toy_id = ?""", (toy_id,)
        )
        total_messages = (await cursor.fetchone())[0]
        
        return {
            "success": True,
            "data": {
                "toy_id": toy_id,
                "toy_name": toy_name,
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "summary_text": summary
            }
        }
    finally:
        await db.close()
