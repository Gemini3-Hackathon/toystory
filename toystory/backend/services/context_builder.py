"""
ToyTalk Backend — ContextWindow 조립
세션 시작 시 Recent Messages + Weekly Summary를 프롬프트에 주입
"""

import json

from config.prompts import CONTEXT_WINDOW_TEMPLATE
from db.database import get_db


async def build_context_window(toy_id: str, max_recent: int = 15) -> str:
    """ContextWindow 조립 — 최근 메시지 + 주간 요약"""
    db = await get_db()

    # 최근 메시지 가져오기 (최대 15개, 토큰 예산 ~500)
    cursor = await db.execute(
        """
        SELECT role, text, created_at
        FROM messages
        WHERE toy_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (toy_id, max_recent),
    )
    rows = await cursor.fetchall()
    recent_messages = list(reversed(rows))  # 시간순으로 정렬

    recent_text = ""
    if recent_messages:
        for msg in recent_messages:
            role_label = "아이" if msg["role"] == "user" else "캐릭터"
            recent_text += f"[{role_label}] {msg['text']}\n"
    else:
        recent_text = "(대화 기록 없음)"

    # 최신 주간 요약 가져오기 (토큰 예산 ~300)
    cursor = await db.execute(
        """
        SELECT week_id, summary, topics, memorable_events
        FROM weekly_summaries
        WHERE toy_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (toy_id,),
    )
    summary_row = await cursor.fetchone()

    week_id = "없음"
    weekly_summary = "(주간 요약 없음)"
    if summary_row:
        week_id = summary_row["week_id"]
        topics = json.loads(summary_row["topics"]) if summary_row["topics"] else []
        events = (
            json.loads(summary_row["memorable_events"])
            if summary_row["memorable_events"]
            else []
        )
        weekly_summary = (
            f"{summary_row['summary']}\n"
            f"주요 화제: {', '.join(topics)}\n"
            f"기억할 일: {', '.join(events)}"
        )

    return CONTEXT_WINDOW_TEMPLATE.format(
        recent_messages=recent_text,
        week_id=week_id,
        weekly_summary=weekly_summary,
    )
