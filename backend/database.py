"""
ToyTalk SQLite Database Setup
5 Tables: parents, children, toys, sessions, messages
"""
import aiosqlite
import os
from config import DATABASE_PATH

DB_PATH = DATABASE_PATH


async def get_db():
    """Get async database connection."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Create all tables if they don't exist."""
    db = await aiosqlite.connect(DB_PATH)
    
    await db.executescript("""
        -- Parents table (simplified — no auth)
        CREATE TABLE IF NOT EXISTS parents (
            id TEXT PRIMARY KEY,
            nickname TEXT NOT NULL DEFAULT '부모님',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Children table
        CREATE TABLE IF NOT EXISTS children (
            id TEXT PRIMARY KEY,
            parent_id TEXT NOT NULL,
            nickname TEXT NOT NULL DEFAULT '아이',
            age INTEGER DEFAULT 5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES parents(id)
        );

        -- Toys table
        CREATE TABLE IF NOT EXISTS toys (
            id TEXT PRIMARY KEY,
            parent_id TEXT NOT NULL,
            name TEXT NOT NULL,
            photo_path TEXT,
            avatar_path TEXT,
            description TEXT,
            personality TEXT,
            color TEXT,
            voice_name TEXT DEFAULT 'Puck',
            system_prompt TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES parents(id)
        );

        -- Sessions table (conversation sessions)
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            toy_id TEXT NOT NULL,
            child_id TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            duration_seconds INTEGER DEFAULT 0,
            message_count INTEGER DEFAULT 0,
            FOREIGN KEY (toy_id) REFERENCES toys(id)
        );

        -- Messages table
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('child', 'character', 'system')),
            content TEXT NOT NULL,
            audio_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    """)
    
    await db.commit()
    await db.close()
    print("✅ Database initialized with 5 tables")


async def seed_db():
    """Insert sample seed data for demo."""
    db = await aiosqlite.connect(DB_PATH)
    
    # Check if seed data exists
    cursor = await db.execute("SELECT COUNT(*) FROM parents")
    count = (await cursor.fetchone())[0]
    
    if count == 0:
        await db.executescript("""
            INSERT INTO parents (id, nickname) VALUES ('parent-001', '데모 부모님');
            INSERT INTO children (id, parent_id, nickname, age) VALUES ('child-001', 'parent-001', '민지', 5);
        """)
        await db.commit()
        print("✅ Seed data inserted")
    else:
        print("ℹ️ Seed data already exists")
    
    await db.close()
