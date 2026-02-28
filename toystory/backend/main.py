"""
ToyTalk Backend — FastAPI 앱 진입점
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from db.database import close_db, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 DB 관리"""
    logger.info("🚀 ToyTalk Backend starting...")
    await init_db()
    logger.info("✅ Database initialized (6 tables)")
    yield
    await close_db()
    logger.info("👋 ToyTalk Backend shutdown")


app = FastAPI(
    title="ToyTalk API",
    description="4-7세 어린이용 AI 장난감 음성 대화 서비스",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (uploads)
import os
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
from routers.auth import router as auth_router
from routers.toys import router as toys_router
from routers.talk import router as talk_router
from routers.tts import router as tts_router
from routers.logs import router as logs_router
from ws.live_proxy import router as ws_router

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(toys_router, prefix=settings.API_PREFIX)
app.include_router(talk_router, prefix=settings.API_PREFIX)
app.include_router(tts_router, prefix=settings.API_PREFIX)
app.include_router(logs_router, prefix=settings.API_PREFIX)
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"service": "ToyTalk API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
