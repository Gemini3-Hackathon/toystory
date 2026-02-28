"""
WebSocket Live Proxy — Adapted from Aiden-Lab server.py
Proxies WebSocket connections between Flutter client and Gemini Live API.
Adds character-specific system prompts.
"""
import asyncio
import json
import ssl
import certifi
import websockets
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from database import get_db

import google.auth
from google.auth.transport.requests import Request

from config import (
    GOOGLE_CLOUD_PROJECT,
    GOOGLE_CLOUD_LOCATION,
    GEMINI_LIVE_MODEL,
    GEMINI_API_HOST,
    GEMINI_LIVE_SERVICE_URL,
)

router = APIRouter()

DEBUG = False


def generate_access_token():
    """Retrieve access token using Google Cloud default credentials."""
    try:
        creds, _ = google.auth.default()
        if not creds.valid:
            creds.refresh(Request())
        return creds.token
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None


async def proxy_messages(source, destination, label: str):
    """Forward messages between two WebSocket connections."""
    try:
        if hasattr(source, '__aiter__'):
            # websockets library connection
            async for message in source:
                try:
                    if isinstance(message, bytes):
                        data = json.loads(message.decode("utf-8"))
                    else:
                        data = json.loads(message)

                    if label == "gemini" and not DEBUG:
                        if "serverContent" in data and "modelTurn" in data["serverContent"]:
                            parts = data["serverContent"]["modelTurn"].get("parts", [])
                            for part in parts:
                                if "text" in part:
                                    print(f"  🤖 AI: {part['text'][:80]}...")
                    
                    # Forward to destination
                    if hasattr(destination, 'send_text'):
                        # FastAPI WebSocket
                        await destination.send_text(json.dumps(data))
                    else:
                        # websockets library
                        await destination.send(json.dumps(data))
                        
                except Exception as e:
                    print(f"⚠️ Error forwarding from {label}: {e}")
        else:
            # FastAPI WebSocket — use receive loop
            while True:
                try:
                    raw = await source.receive_text()
                    data = json.loads(raw)
                    
                    if label == "client" and DEBUG:
                        print(f"📤 Client: {list(data.keys())}")
                    
                    await destination.send(json.dumps(data))
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"⚠️ Error forwarding from {label}: {e}")
                    break
    except Exception as e:
        print(f"❌ Proxy {label} error: {e}")


@router.websocket("/ws/live")
async def websocket_live_proxy(ws: WebSocket):
    """
    WebSocket endpoint that proxies to Gemini Live API.
    
    Protocol:
    1. Client sends setup message with optional toy_id
    2. Server generates access token and connects to Gemini
    3. Bidirectional proxy between client and Gemini
    """
    await ws.accept()
    print("🔌 New WebSocket client connected")
    
    gemini_ws = None
    
    try:
        # Wait for setup message from client
        setup_raw = await asyncio.wait_for(ws.receive_text(), timeout=10.0)
        setup_data = json.loads(setup_raw)
        
        toy_id = setup_data.get("toy_id")
        
        # Get system prompt for the toy
        system_prompt = "너는 친절한 장난감 친구야. 4~7세 어린이와 다정하게 한국어로 대화해."
        voice_name = "Puck"
        
        if toy_id:
            db = await get_db()
            try:
                cursor = await db.execute(
                    "SELECT system_prompt, voice_name FROM toys WHERE id = ?", (toy_id,)
                )
                row = await cursor.fetchone()
                if row:
                    row = dict(row)
                    system_prompt = row.get("system_prompt") or system_prompt
                    voice_name = row.get("voice_name") or voice_name
            finally:
                await db.close()
        
        # Generate access token
        print("🔑 Generating access token...")
        bearer_token = generate_access_token()
        if not bearer_token:
            await ws.send_text(json.dumps({"error": "Authentication failed"}))
            await ws.close(code=1008, reason="Authentication failed")
            return
        print("✅ Access token generated")
        
        # Connect to Gemini Live API
        model_uri = f"projects/{GOOGLE_CLOUD_PROJECT}/locations/{GOOGLE_CLOUD_LOCATION}/publishers/google/models/{GEMINI_LIVE_MODEL}"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        print(f"🔗 Connecting to Gemini Live API...")
        gemini_ws = await websockets.connect(
            GEMINI_LIVE_SERVICE_URL,
            additional_headers=headers,
            ssl=ssl_context,
        )
        print("✅ Connected to Gemini Live API")
        
        # Send setup message to Gemini
        session_setup = {
            "setup": {
                "model": model_uri,
                "generation_config": {
                    "response_modalities": ["AUDIO"],
                    "temperature": 0.8,
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": voice_name,
                            }
                        }
                    },
                    "enable_affective_dialog": True,
                },
                "system_instruction": {
                    "parts": [{"text": system_prompt}]
                },
                "input_audio_transcription": {},
                "output_audio_transcription": {},
                "proactivity": {"proactiveAudio": True},
                "realtime_input_config": {
                    "automatic_activity_detection": {
                        "disabled": False,
                        "silence_duration_ms": 500,
                        "prefix_padding_ms": 500,
                    }
                },
            }
        }
        
        await gemini_ws.send(json.dumps(session_setup))
        print("📨 Session setup sent to Gemini")
        
        # Notify client that setup is complete (pass through Gemini's setupComplete)
        # Start bidirectional proxy
        client_to_gemini = asyncio.create_task(
            proxy_messages(ws, gemini_ws, "client")
        )
        gemini_to_client = asyncio.create_task(
            proxy_messages(gemini_ws, ws, "gemini")
        )
        
        done, pending = await asyncio.wait(
            [client_to_gemini, gemini_to_client],
            return_when=asyncio.FIRST_COMPLETED,
        )
        
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except asyncio.TimeoutError:
        print("⏱️ Timeout waiting for setup message")
    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        if gemini_ws:
            try:
                await gemini_ws.close()
            except Exception:
                pass
        try:
            await ws.close()
        except Exception:
            pass
        print("🔌 WebSocket session ended")
