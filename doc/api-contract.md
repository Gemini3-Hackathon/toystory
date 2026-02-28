# API Contract

> 프론트엔드/백엔드 에이전트가 공통으로 참조하는 API 계약서.
> 이 문서가 Single Source of Truth.

## Base URL

| 환경 | URL |
|------|-----|
| 로컬 개발 | `http://localhost:8000/api/v1` |
| Android 에뮬레이터 | `http://10.0.2.2:8000/api/v1` |

## 공통 규칙

- Content-Type: `application/json`
- 인증: **없음** (MVP — parent_id 파라미터로 구분)

---

## 1. Toys (장난감)

### `POST /api/v1/toys` — 장난감 생성
**Request:**
```json
{ "name": "테디베어", "photo_base64": "base64...", "parent_id": "parent-001" }
```
**Response 200:**
```json
{
  "success": true,
  "data": {
    "id": "abc12345",
    "name": "테디베어",
    "avatar_path": "avatars/abc12345_avatar.png",
    "avatar_base64": "base64...",
    "description": "갈색 곰 인형",
    "personality": "다정하고 호기심 많은 성격",
    "color": "갈색",
    "voice_name": "Puck"
  }
}
```

### `GET /api/v1/toys?parent_id=parent-001` — 장난감 목록
### `GET /api/v1/toys/{toy_id}` — 장난감 상세

---

## 2. Talk (턴제 대화)

### `POST /api/v1/talk`
**Request:**
```json
{ "toy_id": "abc12345", "message": "안녕!", "session_id": null }
```
**Response 200:**
```json
{ "success": true, "data": { "reply": "안녕! 오늘 뭐 했어?", "session_id": "sess-001" } }
```

---

## 3. TTS

### `POST /api/v1/tts` — (Live API에서 네이티브 처리)

---

## 4. Logs (대화 기록)

### `GET /api/v1/logs/{toy_id}` — 세션별 대화 기록

---

## 5. Summary (AI 요약)

### `GET /api/v1/summary/{toy_id}` — AI 대화 요약

---

## 6. WebSocket (실시간 음성)

### `ws://localhost:8000/ws/live`
**Setup Message:**
```json
{ "toy_id": "abc12345" }
```
서버가 Gemini Live API에 연결하고 캐릭터별 시스템 프롬프트를 주입.
이후 양방향 오디오 프록시.

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|-----------|
| 2026-02-28 | 7개 엔드포인트 + WS 구현 완료 |