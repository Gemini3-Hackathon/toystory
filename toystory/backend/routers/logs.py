"""
ToyTalk Backend — Logs 라우터
GET /logs/{toyId} — 날짜별 대화 기록
GET /summary/{toyId} — 주간 요약
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query

from db.database import get_db
from middleware.auth import get_current_user

router = APIRouter(tags=["Logs"])


@router.get("/logs/{toy_id}")
async def get_logs(
    toy_id: str,
    date: str | None = Query(None, description="특정 날짜 (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
):
    """부모용 날짜별 대화 기록"""
    db = await get_db()

    # 소유권 확인
    cursor = await db.execute(
        "SELECT toy_id FROM toys WHERE toy_id = ? AND owner_uid = ?",
        (toy_id, user_id),
    )
    if not await cursor.fetchone():
        raise HTTPException(
            status_code=404,
            detail={"code": "TOY_NOT_FOUND", "message": "장난감을 찾을 수 없습니다"},
        )

    if date:
        cursor = await db.execute(
            "SELECT * FROM daily_logs WHERE toy_id = ? AND date = ? ORDER BY date DESC",
            (toy_id, date),
        )
    else:
        cursor = await db.execute(
            "SELECT * FROM daily_logs WHERE toy_id = ? ORDER BY date DESC LIMIT 30",
            (toy_id,),
        )

    rows = await cursor.fetchall()

    logs = []
    for row in rows:
        conversations = json.loads(row["conversations"]) if row["conversations"] else []
        logs.append(
            {
                "date": row["date"],
                "toyId": row["toy_id"],
                "totalMessages": row["total_messages"],
                "conversations": conversations,
                "isSummarized": bool(row["is_summarized"]),
            }
        )

    return {"success": True, "data": logs}


@router.get("/summary/{toy_id}")
async def get_summary(
    toy_id: str,
    user_id: str = Depends(get_current_user),
):
    """주간 요약"""
    db = await get_db()

    # 소유권 확인
    cursor = await db.execute(
        "SELECT toy_id FROM toys WHERE toy_id = ? AND owner_uid = ?",
        (toy_id, user_id),
    )
    if not await cursor.fetchone():
        raise HTTPException(
            status_code=404,
            detail={"code": "TOY_NOT_FOUND", "message": "장난감을 찾을 수 없습니다"},
        )

    cursor = await db.execute(
        """SELECT * FROM weekly_summaries WHERE toy_id = ?
           ORDER BY created_at DESC LIMIT 4""",
        (toy_id,),
    )
    rows = await cursor.fetchall()

    summaries = []
    for row in rows:
        date_range = json.loads(row["date_range"]) if row["date_range"] else {}
        topics = json.loads(row["topics"]) if row["topics"] else []
        emotions = json.loads(row["emotions"]) if row["emotions"] else []
        memorable = json.loads(row["memorable_events"]) if row["memorable_events"] else []

        summaries.append(
            {
                "weekId": row["week_id"],
                "toyId": row["toy_id"],
                "dateRange": date_range,
                "totalSessions": row["total_sessions"],
                "totalMessages": row["total_messages"],
                "summary": row["summary"],
                "topics": topics,
                "emotions": emotions,
                "memorableEvents": memorable,
            }
        )

    return {"success": True, "data": summaries}
