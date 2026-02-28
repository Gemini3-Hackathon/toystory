#!/bin/bash
# ToyTalk Backend 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "🧸 ToyTalk Backend 시작..."

# 1. venv 생성 (없으면)
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv "$BACKEND_DIR/venv"
fi

# 2. 가상환경 활성화
source "$BACKEND_DIR/venv/bin/activate"

# 3. 의존성 설치
echo "📦 패키지 설치 중..."
pip install -r "$BACKEND_DIR/requirements.txt" --quiet

# 4. 서버 실행
echo "🚀 서버 시작..."
cd "$BACKEND_DIR"
python main.py
