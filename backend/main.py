"""
ToyTalk Backend — FastAPI Main Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import HOST, PORT, CORS_ORIGINS, UPLOAD_DIR, AVATAR_DIR
from database import init_db, seed_db

# Routers
from routers.toys import router as toys_router
from routers.talk import router as talk_router
from routers.tts import router as tts_router
from routers.logs import router as logs_router
from routers.summary import router as summary_router
from ws.live_proxy import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown."""
    # Startup
    print("🚀 ToyTalk Backend starting...")
    await init_db()
    await seed_db()
    
    # Create upload directories
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(AVATAR_DIR, exist_ok=True)
    
    print(f"""
╔════════════════════════════════════════════════╗
║         🧸 ToyTalk Backend Server              ║
╠════════════════════════════════════════════════╣
║                                                ║
║  🌐 REST API: http://localhost:{PORT}/api/v1    ║
║  🔌 WebSocket: ws://localhost:{PORT}/ws/live    ║
║  📚 API Docs: http://localhost:{PORT}/docs      ║
║                                                ║
╚════════════════════════════════════════════════╝
""")
    yield
    # Shutdown
    print("👋 ToyTalk Backend shutting down...")


app = FastAPI(
    title="ToyTalk API",
    description="AI-powered toy conversation platform for children",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads/avatars
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AVATAR_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/avatars", StaticFiles(directory=AVATAR_DIR), name="avatars")

# Mount web app (Talk screen) static files
WEB_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "dist")
if os.path.exists(WEB_DIR):
    app.mount("/talk-web", StaticFiles(directory=WEB_DIR, html=True), name="talk-web")

# Register REST routers
app.include_router(toys_router, prefix="/api/v1")
app.include_router(talk_router, prefix="/api/v1")
app.include_router(tts_router, prefix="/api/v1")
app.include_router(logs_router, prefix="/api/v1")
app.include_router(summary_router, prefix="/api/v1")

# Register WebSocket router
app.include_router(ws_router)


@app.get("/")
async def root():
    return {
        "service": "ToyTalk API",
        "version": "1.0.0",
        "endpoints": {
            "api_docs": "/docs",
            "toys": "/api/v1/toys",
            "talk": "/api/v1/talk",
            "tts": "/api/v1/tts",
            "logs": "/api/v1/logs/{toy_id}",
            "summary": "/api/v1/summary/{toy_id}",
            "websocket": "/ws/live",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
