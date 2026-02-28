"""
ToyTalk Backend — SQLite 데이터베이스 모듈
aiosqlite 기반 비동기 DB 연결 + DDL 자동 실행
"""

import aiosqlite
from config.settings import settings

# 전역 DB 연결
_db: aiosqlite.Connection | None = None

DDL_STATEMENTS = [
    # toys: 캐릭터(장난감) 루트
    """
    CREATE TABLE IF NOT EXISTS toys (
        toy_id TEXT PRIMARY KEY,
        owner_uid TEXT NOT NULL,
        toy_name TEXT NOT NULL,
        type TEXT,
        primary_color TEXT,
        secondary_color TEXT,
        features TEXT,
        expression TEXT,
        texture TEXT,
        voice_profile TEXT,
        child_name TEXT,
        avatar_path TEXT,
        original_photo_path TEXT,
        style_preset TEXT DEFAULT 'cel_shading',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # sessions: 대화 세션
    """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        toy_id TEXT NOT NULL REFERENCES toys(toy_id) ON DELETE CASCADE,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_message_at TIMESTAMP,
        message_count INTEGER DEFAULT 0
    )
    """,
    # messages: 개별 메시지
    """
    CREATE TABLE IF NOT EXISTS messages (
        message_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
        toy_id TEXT NOT NULL REFERENCES toys(toy_id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
        text TEXT NOT NULL,
        audio_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # daily_logs: 일단위 집계
    """
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        toy_id TEXT NOT NULL REFERENCES toys(toy_id) ON DELETE CASCADE,
        total_messages INTEGER DEFAULT 0,
        conversations TEXT NOT NULL,
        is_summarized BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date, toy_id)
    )
    """,
    # weekly_summaries: 주간 요약
    """
    CREATE TABLE IF NOT EXISTS weekly_summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week_id TEXT NOT NULL,
        toy_id TEXT NOT NULL REFERENCES toys(toy_id) ON DELETE CASCADE,
        date_range TEXT NOT NULL,
        total_sessions INTEGER DEFAULT 0,
        total_messages INTEGER DEFAULT 0,
        summary TEXT NOT NULL,
        topics TEXT,
        emotions TEXT,
        memorable_events TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(week_id, toy_id)
    )
    """,
    # users: 사용자
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nickname TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
]


async def init_db() -> aiosqlite.Connection:
    """DB 연결 생성 + DDL 실행"""
    global _db
    _db = await aiosqlite.connect(settings.DB_PATH)
    _db.row_factory = aiosqlite.Row
    await _db.execute("PRAGMA journal_mode=WAL")
    await _db.execute("PRAGMA foreign_keys=ON")

    for ddl in DDL_STATEMENTS:
        await _db.execute(ddl)
    await _db.commit()

    return _db


async def get_db() -> aiosqlite.Connection:
    """현재 DB 연결 반환"""
    if _db is None:
        return await init_db()
    return _db


async def close_db():
    """DB 연결 종료"""
    global _db
    if _db:
        await _db.close()
        _db = None
