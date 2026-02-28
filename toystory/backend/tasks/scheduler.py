"""
ToyTalk Backend — Background Tasks (APScheduler)
- aggregateDailyLogs: 매일 00:00 — messages → daily_logs 집계
- generateWeeklySummary: 매주 월 01:00 — daily_logs → Gemini → weekly_summaries
"""

import json
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)


async def aggregate_daily_logs():
    """메시지를 daily_logs로 일별 집계"""
    from db.database import get_db

    try:
        db = await get_db()
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

        # 어제 메시지가 있는 toy 목록
        cursor = await db.execute(
            """SELECT DISTINCT toy_id FROM messages
               WHERE DATE(created_at) = ?""",
            (yesterday,),
        )
        toy_ids = [row["toy_id"] for row in await cursor.fetchall()]

        for toy_id in toy_ids:
            cursor = await db.execute(
                """SELECT role, text, TIME(created_at) as time
                   FROM messages WHERE toy_id = ? AND DATE(created_at) = ?
                   ORDER BY created_at""",
                (toy_id, yesterday),
            )
            messages = await cursor.fetchall()

            conversations = [
                {"time": msg["time"], "role": msg["role"], "text": msg["text"]}
                for msg in messages
            ]

            await db.execute(
                """INSERT OR REPLACE INTO daily_logs (date, toy_id, total_messages, conversations)
                   VALUES (?, ?, ?, ?)""",
                (yesterday, toy_id, len(conversations), json.dumps(conversations, ensure_ascii=False)),
            )

        await db.commit()
        logger.info(f"Daily logs aggregated for {len(toy_ids)} toys on {yesterday}")

    except Exception as e:
        logger.error(f"Daily log aggregation failed: {e}")


async def generate_weekly_summary():
    """daily_logs → Gemini → weekly_summaries 생성"""
    from db.database import get_db

    try:
        db = await get_db()

        now = datetime.now(timezone.utc)
        week_start = (now - timedelta(days=now.weekday() + 7)).strftime("%Y-%m-%d")
        week_end = (now - timedelta(days=now.weekday() + 1)).strftime("%Y-%m-%d")
        week_id = (now - timedelta(days=7)).strftime("%Y-W%W")

        # 지난 주 daily_logs가 있는 toy
        cursor = await db.execute(
            """SELECT DISTINCT toy_id FROM daily_logs
               WHERE date BETWEEN ? AND ? AND is_summarized = 0""",
            (week_start, week_end),
        )
        toy_ids = [row["toy_id"] for row in await cursor.fetchall()]

        for toy_id in toy_ids:
            cursor = await db.execute(
                """SELECT date, conversations, total_messages
                   FROM daily_logs WHERE toy_id = ? AND date BETWEEN ? AND ?
                   ORDER BY date""",
                (toy_id, week_start, week_end),
            )
            logs = await cursor.fetchall()

            total_messages = sum(row["total_messages"] for row in logs)

            # Gemini로 요약 생성
            try:
                from google import genai
                from config.settings import settings
                from config.prompts import WEEKLY_SUMMARY_PROMPT

                client = genai.Client(
                    vertexai=True,
                    project=settings.GOOGLE_CLOUD_PROJECT,
                    location=settings.GOOGLE_CLOUD_LOCATION,
                )

                logs_text = json.dumps(
                    [{"date": r["date"], "conversations": json.loads(r["conversations"])} for r in logs],
                    ensure_ascii=False,
                )

                response = client.models.generate_content(
                    model=settings.GEMINI_FLASH_MODEL,
                    contents=f"{WEEKLY_SUMMARY_PROMPT}\n\n{logs_text}",
                )

                summary_data = json.loads(response.text.strip())

            except Exception as e:
                logger.error(f"Weekly summary generation failed for {toy_id}: {e}")
                summary_data = {
                    "summary": "이번 주 아이는 캐릭터와 즐겁게 대화했습니다.",
                    "topics": [],
                    "emotions": [],
                    "memorableEvents": [],
                }

            await db.execute(
                """INSERT OR REPLACE INTO weekly_summaries
                   (week_id, toy_id, date_range, total_sessions, total_messages,
                    summary, topics, emotions, memorable_events)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    week_id,
                    toy_id,
                    json.dumps({"start": week_start, "end": week_end}),
                    len(logs),
                    total_messages,
                    summary_data.get("summary", ""),
                    json.dumps(summary_data.get("topics", []), ensure_ascii=False),
                    json.dumps(summary_data.get("emotions", []), ensure_ascii=False),
                    json.dumps(summary_data.get("memorableEvents", []), ensure_ascii=False),
                ),
            )

            # daily_logs에 is_summarized 표시
            await db.execute(
                "UPDATE daily_logs SET is_summarized = 1 WHERE toy_id = ? AND date BETWEEN ? AND ?",
                (toy_id, week_start, week_end),
            )

        await db.commit()
        logger.info(f"Weekly summaries generated for {len(toy_ids)} toys")

    except Exception as e:
        logger.error(f"Weekly summary generation failed: {e}")
