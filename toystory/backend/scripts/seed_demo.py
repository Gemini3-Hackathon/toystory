"""
ToyTalk Backend — Phase 9: 데모 시드 데이터
해커톤 데모용 더미 데이터 삽입
"""

import asyncio
import json
import uuid
from datetime import datetime, timezone, timedelta

from db.database import init_db, close_db
from middleware.auth import hash_password


async def seed_demo_data():
    """데모용 시드 데이터 삽입"""
    db = await init_db()

    # 1. 데모 사용자
    user_id = "demo-user-001"
    now = datetime.now(timezone.utc).isoformat()

    await db.execute(
        "INSERT OR IGNORE INTO users (user_id, email, password_hash, nickname, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, "demo@toytalk.ai", hash_password("demo1234"), "데모 가족", now),
    )

    # 2. 데모 장난감 3개
    toys = [
        {
            "toy_id": "demo-bear",
            "toy_name": "곰돌이",
            "type": "bear",
            "primary_color": "#8B4513",
            "features": ["큰 눈", "리본", "갈색 털"],
            "expression": "smiling",
            "texture": "plush_fuzzy",
            "voice_profile": {
                "style": "ppororo",
                "pitchShift": 3,
                "speedRate": 1.0,
                "ttsPrompt": "따뜻하고 포근한, 밝은 목소리",
            },
            "child_name": "서연",
        },
        {
            "toy_id": "demo-dino",
            "toy_name": "공룡이",
            "type": "dinosaur",
            "primary_color": "#228B22",
            "features": ["뿔", "날개", "초록색"],
            "expression": "excited",
            "texture": "plastic_smooth",
            "voice_profile": {
                "style": "tayo",
                "pitchShift": 1,
                "speedRate": 1.1,
                "ttsPrompt": "또박또박하고 에너지 넘치는",
            },
            "child_name": "민준",
        },
        {
            "toy_id": "demo-rabbit",
            "toy_name": "토끼",
            "type": "doll",
            "primary_color": "#FFB6C1",
            "features": ["긴 귀", "분홍색 코", "하트 무늬"],
            "expression": "smiling",
            "texture": "plush_fuzzy",
            "voice_profile": {
                "style": "disney",
                "pitchShift": 2,
                "speedRate": 1.0,
                "ttsPrompt": "부드럽고 상냥한, 노래하듯",
            },
            "child_name": "하은",
        },
    ]

    for toy in toys:
        await db.execute(
            """INSERT OR IGNORE INTO toys (toy_id, owner_uid, toy_name, type, primary_color,
               secondary_color, features, expression, texture, voice_profile, child_name, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                toy["toy_id"], user_id, toy["toy_name"], toy["type"],
                toy["primary_color"], "#FFFFFF",
                json.dumps(toy["features"]),
                toy["expression"], toy["texture"],
                json.dumps(toy["voice_profile"]),
                toy["child_name"], now,
            ),
        )

    # 3. 데모 대화 세션 (곰돌이)
    session_id = "demo-session-001"
    await db.execute(
        "INSERT OR IGNORE INTO sessions (session_id, toy_id, started_at, message_count) VALUES (?, ?, ?, ?)",
        (session_id, "demo-bear", now, 6),
    )

    demo_messages = [
        ("user", "안녕 곰돌이!"),
        ("assistant", "와~ 안녕! 오늘 기분이 어때? 😊"),
        ("user", "오늘 유치원에서 그림 그렸어!"),
        ("assistant", "우와! 정말? 무슨 그림 그렸어? 너무 궁금해~"),
        ("user", "우리 가족 그렸어! 엄마 아빠 나!"),
        ("assistant", "와~ 가족 그림이라니, 정말 멋지다! 곰돌이도 그려줘~ 🎨"),
    ]

    base_time = datetime.now(timezone.utc) - timedelta(hours=1)
    for i, (role, text) in enumerate(demo_messages):
        msg_time = (base_time + timedelta(minutes=i * 2)).isoformat()
        await db.execute(
            "INSERT OR IGNORE INTO messages (message_id, session_id, toy_id, role, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (f"demo-msg-{i:03d}", session_id, "demo-bear", role, text, msg_time),
        )

    # 4. 데모 daily_log
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    demo_conversations = [{"role": r, "text": t} for r, t in demo_messages]
    await db.execute(
        "INSERT OR IGNORE INTO daily_logs (date, toy_id, total_messages, conversations) VALUES (?, ?, ?, ?)",
        (yesterday, "demo-bear", len(demo_messages), json.dumps(demo_conversations, ensure_ascii=False)),
    )

    # 5. 데모 weekly_summary
    week_id = datetime.now(timezone.utc).strftime("%Y-W%W")
    await db.execute(
        """INSERT OR IGNORE INTO weekly_summaries
           (week_id, toy_id, date_range, total_sessions, total_messages,
            summary, topics, emotions, memorable_events)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            week_id, "demo-bear",
            json.dumps({"start": yesterday, "end": yesterday}),
            1, 6,
            "이번 주 서연이는 곰돌이와 유치원에서 있었던 일에 대해 이야기했습니다. 특히 가족 그림을 그린 것을 자랑스러워하며 곰돌이에게 이야기했어요. 아이는 밝고 긍정적인 감정을 보여주었습니다.",
            json.dumps(["유치원", "그림 그리기", "가족"], ensure_ascii=False),
            json.dumps(["행복", "자랑스러움", "즐거움"], ensure_ascii=False),
            json.dumps(["가족 그림을 그려서 자랑함", "곰돌이에게도 그려달라고 약속"], ensure_ascii=False),
        ),
    )

    await db.commit()
    print("✅ 데모 시드 데이터 삽입 완료!")
    print(f"   - 사용자: demo@toytalk.ai / demo1234")
    print(f"   - 장난감: 곰돌이, 공룡이, 토끼 (3개)")
    print(f"   - 대화: 6개 메시지 (곰돌이 세션)")
    print(f"   - 주간 요약: {week_id}")

    await close_db()


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
