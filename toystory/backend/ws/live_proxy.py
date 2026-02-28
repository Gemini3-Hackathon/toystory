"""
ToyTalk Backend — Gemini Live API WebSocket Proxy (Phase 5 구현)
Flutter ↔ Backend WS ↔ Vertex AI Live API 양방향 오디오 프록시
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from config.prompts import build_system_instruction
from config.settings import settings
from db.database import get_db
from middleware.safety import check_safety, SAFE_FALLBACK

logger = logging.getLogger(__name__)

router = APIRouter()


class LiveSession:
    """단일 Live API 세션 관리"""

    def __init__(self, toy_id: str, session_id: str, toy_name: str, toy_type: str):
        self.toy_id = toy_id
        self.session_id = session_id
        self.toy_name = toy_name
        self.toy_type = toy_type
        self.vertex_ws = None
        self.connected = False

    async def connect_to_vertex(self):
        """Vertex AI Live API에 WebSocket 연결"""
        try:
            from google import genai

            client = genai.Client(
                vertexai=True,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION,
            )

            system_instruction = build_system_instruction(
                toy_name=self.toy_name,
                toy_type=self.toy_type,
            )

            config = {
                "response_modalities": ["AUDIO"],
                "system_instruction": system_instruction,
            }

            self.vertex_ws = client.aio.live.connect(
                model=settings.GEMINI_LIVE_MODEL,
                config=config,
            )
            self.connected = True
            logger.info(f"Connected to Vertex Live API: session={self.session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Vertex Live API: {e}")
            self.connected = False
            return False

    async def close(self):
        """연결 종료"""
        self.connected = False
        if self.vertex_ws:
            try:
                await self.vertex_ws.__aexit__(None, None, None)
            except Exception:
                pass
            self.vertex_ws = None


@router.websocket("/ws/live")
async def live_proxy(
    websocket: WebSocket,
    toyId: str = Query(...),
    sessionId: str = Query(None),
):
    """Vertex Live API 양방향 오디오 프록시"""
    await websocket.accept()

    session_id = sessionId or str(uuid.uuid4())
    logger.info(f"WS connected: toyId={toyId}, sessionId={session_id}")

    # 장난감 정보 조회
    db = await get_db()
    cursor = await db.execute(
        "SELECT toy_name, type FROM toys WHERE toy_id = ?", (toyId,)
    )
    toy = await cursor.fetchone()

    if not toy:
        await websocket.send_json({
            "type": "error",
            "message": "장난감을 찾을 수 없습니다",
        })
        await websocket.close()
        return

    # 세션 생성/확인
    cursor = await db.execute(
        "SELECT session_id FROM sessions WHERE session_id = ?", (session_id,)
    )
    if not await cursor.fetchone():
        now = datetime.now(timezone.utc).isoformat()
        await db.execute(
            "INSERT INTO sessions (session_id, toy_id, started_at) VALUES (?, ?, ?)",
            (session_id, toyId, now),
        )
        await db.commit()

    # Live 세션 생성
    live = LiveSession(
        toy_id=toyId,
        session_id=session_id,
        toy_name=toy["toy_name"],
        toy_type=toy["type"] or "default",
    )

    # Vertex Live API 연결 시도
    vertex_connected = await live.connect_to_vertex()

    if vertex_connected:
        await websocket.send_json({
            "type": "session_started",
            "sessionId": session_id,
            "mode": "live",
        })

        # 양방향 프록시 실행
        try:
            async with live.vertex_ws as vertex_session:
                # 클라이언트 → Vertex 전달 태스크
                async def client_to_vertex():
                    try:
                        while True:
                            data = await websocket.receive()

                            if "bytes" in data:
                                # 오디오 프레임 → Vertex
                                await vertex_session.send(
                                    input={"data": data["bytes"], "mime_type": "audio/pcm;rate=16000"},
                                    end_of_turn=False,
                                )

                            elif "text" in data:
                                msg = json.loads(data["text"])
                                msg_type = msg.get("type", "")

                                if msg_type == "end_of_turn":
                                    await vertex_session.send(
                                        input=None,
                                        end_of_turn=True,
                                    )
                                elif msg_type == "interrupt":
                                    # 바지인 (재생 중단)
                                    logger.info("Barge-in interrupt received")
                                    await websocket.send_json({
                                        "type": "interrupted",
                                    })
                                elif msg_type == "text":
                                    # 텍스트 메시지 → 안전 필터 → Vertex
                                    text = msg.get("text", "")
                                    safety = check_safety(text)
                                    if not safety["safe"]:
                                        await websocket.send_json({
                                            "type": "transcript",
                                            "role": "assistant",
                                            "text": SAFE_FALLBACK,
                                        })
                                    else:
                                        await vertex_session.send(
                                            input=text,
                                            end_of_turn=True,
                                        )
                                elif msg_type == "ping":
                                    await websocket.send_json({"type": "pong"})

                    except WebSocketDisconnect:
                        logger.info("Client disconnected")
                    except Exception as e:
                        logger.error(f"Client→Vertex error: {e}")

                # Vertex → 클라이언트 전달 태스크
                async def vertex_to_client():
                    try:
                        async for response in vertex_session.receive():
                            if response.data:
                                # 오디오 응답 → 클라이언트
                                await websocket.send_bytes(response.data)
                            elif response.text:
                                # 텍스트 응답 → 클라이언트
                                # 안전 필터 (출력)
                                safety = check_safety(response.text)
                                text = SAFE_FALLBACK if not safety["safe"] else response.text

                                await websocket.send_json({
                                    "type": "transcript",
                                    "role": "assistant",
                                    "text": text,
                                })

                                # 메시지 저장
                                now = datetime.now(timezone.utc).isoformat()
                                msg_id = str(uuid.uuid4())
                                await db.execute(
                                    "INSERT INTO messages (message_id, session_id, toy_id, role, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                                    (msg_id, session_id, toyId, "assistant", text, now),
                                )
                                await db.execute(
                                    "UPDATE sessions SET last_message_at = ?, message_count = message_count + 1 WHERE session_id = ?",
                                    (now, session_id),
                                )
                                await db.commit()

                            if response.server_content and response.server_content.turn_complete:
                                await websocket.send_json({
                                    "type": "turn_complete",
                                })

                    except Exception as e:
                        logger.error(f"Vertex→Client error: {e}")

                # 양방향 동시 실행
                await asyncio.gather(
                    client_to_vertex(),
                    vertex_to_client(),
                    return_exceptions=True,
                )
        except Exception as e:
            logger.error(f"Live session error: {e}")

    else:
        # Live API 연결 실패 → 폴백 (턴제 모드)
        await websocket.send_json({
            "type": "session_started",
            "sessionId": session_id,
            "mode": "fallback",
            "message": "Live API 연결에 실패하여 턴제 모드로 전환합니다.",
        })

        try:
            while True:
                data = await websocket.receive()

                if "text" in data:
                    msg = json.loads(data["text"])
                    msg_type = msg.get("type", "")

                    if msg_type == "text":
                        text = msg.get("text", "")

                        # 턴제 폴백 응답
                        from services.gemini_chat import chat_with_gemini
                        from services.context_builder import build_context_window

                        context_window = await build_context_window(toyId)
                        reply = await chat_with_gemini(
                            toy_name=toy["toy_name"],
                            toy_type=toy["type"] or "default",
                            user_text=text,
                            context_window=context_window,
                        )

                        # 메시지 저장
                        now = datetime.now(timezone.utc).isoformat()
                        for role, t in [("user", text), ("assistant", reply)]:
                            msg_id = str(uuid.uuid4())
                            await db.execute(
                                "INSERT INTO messages (message_id, session_id, toy_id, role, text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                                (msg_id, session_id, toyId, role, t, now),
                            )
                        await db.execute(
                            "UPDATE sessions SET last_message_at = ?, message_count = message_count + 2 WHERE session_id = ?",
                            (now, session_id),
                        )
                        await db.commit()

                        await websocket.send_json({
                            "type": "transcript",
                            "role": "assistant",
                            "text": reply,
                        })
                        await websocket.send_json({"type": "turn_complete"})

                    elif msg_type == "ping":
                        await websocket.send_json({"type": "pong"})

                elif "bytes" in data:
                    # 턴제 모드에서는 오디오 무시
                    await websocket.send_json({
                        "type": "info",
                        "message": "턴제 모드에서는 텍스트 입력만 지원됩니다.",
                    })

        except WebSocketDisconnect:
            logger.info(f"WS disconnected: toyId={toyId}, sessionId={session_id}")
        except Exception as e:
            logger.error(f"Fallback WS error: {e}")

    await live.close()
    logger.info(f"Live session ended: session={session_id}")
