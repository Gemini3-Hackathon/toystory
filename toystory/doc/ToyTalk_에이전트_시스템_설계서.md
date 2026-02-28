# ToyTalk 에이전트 시스템 설계서

> Claude Code / Codex 듀얼 호환 에이전트 아키텍처
> 본 문서는 `ToyTalk_최종_통합_명세서_v1.1.md`를 구현하기 위한 에이전트 계획서입니다.

---

## 1. 작업 컨텍스트

### 1.1 배경

ToyTalk은 4~7세 어린이가 자신의 장난감을 AI 캐릭터로 변환하고 음성 대화하는 서비스다.
Google Gemini 3 해커톤(1일 스프린트) 출품작이며, 데모 가능한 MVP를 최우선으로 한다.

### 1.2 목적

최종 통합 명세서(v1.1)에 정의된 Phase 0~9를 **에이전트가 순차 구현**할 수 있도록,
워크플로우·역할 분담·스킬·검증 기준을 설계한다.

### 1.3 범위

| 영역 | 포함 | 제외 |
|------|------|------|
| **Backend** | FastAPI + SQLite + Vertex AI 연동 + WS Proxy + Background Tasks | 프로덕션 DB 마이그레이션(PostgreSQL) |
| **Frontend** | Flutter 4화면 (MyToys, CreateToy, Talk, Parent) + Audio I/O + WS | iOS 배포, 웹 빌드 |
| **AI/Prompt** | 3층 프롬프트, 음성 매칭, ContextWindow, 이미지 생성 파이프라인 | 모델 파인튜닝 |
| **Infra** | Dockerfile, Cloud Run 배포 커맨드 | CI/CD 파이프라인, 모니터링 |

### 1.4 입출력 정의

| 항목 | 내용 |
|------|------|
| **Input** | 최종 통합 명세서 v1.1 (doc/unified-spec.md) + API Contract (doc/api-contract.md) |
| **Output** | 실행 가능한 Flutter 앱 + FastAPI 서버 + Dockerfile + 데모 데이터 |

### 1.5 제약조건

| ID | 제약 |
|----|------|
| **T-1** | 해커톤 1일 스프린트 — P0 항목은 8시간 내 완료 가능해야 함 |
| **T-2** | Android 에뮬레이터에서 데모 가능해야 함 |
| **T-3** | Vertex AI API 호출 비용 $5 이내 |
| **T-4** | 단일 Cloud Run 인스턴스 (max=1)로 동작 |
| **T-5** | 모든 코드는 `flutter analyze` 0 error, `python -m py_compile` pass |

### 1.6 우선순위 태깅 체계

| Tag | 의미 | 기준 |
|-----|------|------|
| **P0** | 해커톤 데모 필수 | 없으면 데모 불가 |
| **P1** | 데모 임팩트 강화 | 있으면 심사 점수 상승 |
| **P2** | 완성도 | 프로덕션 대비 |

### 1.7 용어 정의

| 용어 | 정의 |
|------|------|
| **Toy** | 장난감 기반 AI 캐릭터 (SQLite toys 테이블 1행) |
| **Session** | 1회 대화 세션 (WS 연결 ~ 해제) |
| **ContextWindow** | 세션 시작 시 프롬프트에 주입되는 기억 컨텍스트 (~900 tokens) |
| **Stage 1/2/3** | 이미지 생성 파이프라인 단계 (분석/생성/검증) |
| **3층 프롬프트** | SYSTEM + PERSONA + SAFETY 프롬프트 스택 |
| **Barge-in** | 아이가 캐릭터 발화 도중 끼어드는 인터럽트 |
| **Live API** | Vertex AI Multimodal Live API (실시간 음성↔음성 WebSocket) |

---

## 2. 워크플로우 정의

### 2.1 전체 Phase 흐름

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4
(환경준비)   (Flutter앱)  (백엔드)    (이미지생성)  (턴제대화)
  [P0]        [P0]        [P0]        [P0]         [P0]
    │           │           │           │            │
    ▼           ▼           ▼           ▼            ▼
Phase 5 ──→ Phase 6 ──→ Phase 7 ──→ Phase 8 ──→ Phase 9
(Live API)  (라이브러리) (부모화면)   (최적화)     (데모준비)
  [P0]        [P1]        [P1]        [P2]         [P0]
```

### 2.2 Phase별 워크플로우 상세

---

#### Phase 0: 환경 준비 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 방법 | 실패 처리 |
|---|------|-----------|------|-----------|-----------|-----------|
| 0.1 | Flutter 환경 확인 | 스크립트 | `flutter doctor -v` 실행 | Android toolchain ✅ | 규칙 기반 (exit code 0) | 에스컬레이션 (수동 설치 안내) |
| 0.2 | Flutter 프로젝트 생성 | 스크립트 | `flutter create --platforms android,ios toytalk_app` | pubspec.yaml 존재 | 스키마 검증 | 자동 재시도 (1회) |
| 0.3 | 패키지 설치 | 스크립트 | pubspec.yaml 편집 + `flutter pub get` | 의존성 resolve 성공 | 규칙 기반 (exit code) | 자동 재시도 (2회) |
| 0.4 | Backend 프로젝트 생성 | 스크립트 | 디렉토리 생성 + requirements.txt + `pip install` | import fastapi 성공 | 규칙 기반 | 자동 재시도 (1회) |
| 0.5 | SQLite 초기화 | 스크립트 | DDL 실행 → 5개 테이블 생성 | 테이블 5개 존재 | 스키마 검증 (`sqlite3 .tables`) | 자동 재시도 (1회) |
| 0.6 | 에뮬레이터 확인 | 스크립트 | `flutter devices` | 1개 이상 디바이스 | 규칙 기반 | 에스컬레이션 |

**Flutter 필수 패키지:**
```
http, web_socket_channel, flutter_sound, just_audio,
provider, image_picker, path_provider, uuid
```

**Python 필수 패키지:**
```
fastapi, uvicorn[standard], aiosqlite, pyjwt, apscheduler,
google-genai, python-multipart, httpx
```

---

#### Phase 1: Flutter MVP 앱 구축 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 1.1 | 폴더 구조 생성 | 스크립트 | lib/ 하위 Clean Architecture 디렉토리 | 디렉토리 존재 | 스키마 | 재시도 |
| 1.2 | 모델 클래스 | 에이전트 | api-contract.md 기반 Dart 모델 생성 | fromJson/toJson 구현 | 규칙 (analyze) | 재시도(2) |
| 1.3 | API 서비스 | 에이전트 | http 패키지 기반 REST 클라이언트 | 엔드포인트 7개 메서드 | 규칙 (analyze) | 재시도(2) |
| 1.4 | MyToys 화면 | 에이전트 | GridView + ToyCard 위젯 | 화면 렌더링 성공 | 규칙 (빌드 성공) | 재시도(2) |
| 1.5 | CreateToy 화면 | 에이전트 | Camera/Gallery + Upload UI | image_picker 동작 | 규칙 (빌드) | 재시도(2) |
| 1.6 | Talk 화면 (기본) | 에이전트 | 채팅 버블 + 녹음 버튼 UI | 화면 렌더링 | 규칙 (빌드) | 재시도(2) |
| 1.7 | Parent 화면 (기본) | 에이전트 | PageView + 대화 슬라이드 UI | 화면 렌더링 | 규칙 (빌드) | 재시도(2) |
| 1.8 | 라우팅 설정 | 에이전트 | Navigator 또는 GoRouter 설정 | 4화면 전환 성공 | 규칙 (빌드) | 재시도(2) |
| 1.9 | 통합 검증 | 스크립트 | `flutter analyze` + `flutter build apk --debug` | 0 error | 규칙 기반 | 에스컬레이션 |

---

#### Phase 2: 백엔드 구성 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 2.1 | FastAPI 앱 뼈대 | 에이전트 | main.py + routers + middleware + db | 서버 기동 성공 | 규칙 (`curl /docs`) | 재시도(2) |
| 2.2 | DB 초기화 모듈 | 에이전트 | db/database.py — aiosqlite + DDL | 테이블 5개 자동 생성 | 스키마 검증 | 재시도(2) |
| 2.3 | 인증 미들웨어 | 에이전트 | middleware/auth.py — PyJWT 발급/검증 | 토큰 발급→검증 성공 | 규칙 (pytest) | 재시도(2) |
| 2.4 | Toys CRUD API | 에이전트 | routers/toys.py — POST/GET | 201 + 200 응답 | 규칙 (curl 테스트) | 재시도(2) |
| 2.5 | Talk API | 에이전트 | routers/talk.py — POST /talk | Gemini 응답 반환 | 규칙 (curl) | 재시도(2) |
| 2.6 | Logs API | 에이전트 | routers/logs.py — GET /logs, /summary | JSON 응답 | 규칙 (curl) | 재시도(2) |
| 2.7 | 안전 필터 | 에이전트 | middleware/safety.py — 2단계 필터 | 위험 입력 차단 | 규칙 (테스트 케이스) | 재시도(2) |
| 2.8 | 프롬프트 템플릿 | 에이전트 | config/prompts.py — 3층 프롬프트 | 변수 치환 정상 | LLM 자기검증 | 재시도(2) |
| 2.9 | Dockerfile | 스크립트 | python:3.12-slim 기반 | `docker build` 성공 | 규칙 (exit code) | 재시도(1) |
| 2.10 | 통합 테스트 | 스크립트 | 서버 기동 + 주요 API curl | 5개 엔드포인트 200/201 | 규칙 기반 | 에스컬레이션 |

---

#### Phase 3: 캐릭터 이미지 생성 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 3.1 | Stage 1 — 장난감 분석 | 에이전트 | Gemini Vision API 호출 → JSON 추출 | type, colors, features 추출 | 스키마 (JSON 필드 존재) | 재시도(2) |
| 3.2 | Stage 2 — 아바타 생성 | 에이전트 | 분석 결과 → Gemini ImageGen 프롬프트 조립 | 이미지 파일 생성 | 규칙 (파일 존재 + 크기 > 0) | 재시도(2) |
| 3.3 | Stage 3 — 품질 검증 | 에이전트 | 생성 이미지 재분석 → 스코어 비교 | color_match ≥ 0.85 | 규칙 기반 | 재시도(2) → 3회 실패 시 원본 사용 |
| 3.4 | 음성 프로파일 자동 매칭 | 에이전트 | toy.type → voiceProfile JSON 생성 | voice_profile INSERT 완료 | 스키마 (필수 5필드) | 재시도(1) |
| 3.5 | CreateToy 화면 연동 | 에이전트 | Flutter 업로드 → API → 결과 표시 | 사진→아바타 E2E 성공 | 사람 검토 (데모) | 에스컬레이션 |

---

#### Phase 4: 턴제 대화 기능 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 4.1 | 오디오 녹음 | 에이전트 | flutter_sound — PCM 16kHz/16bit/mono | 녹음 파일 생성 | 규칙 (파일 크기) | 재시도(2) |
| 4.2 | POST /talk 연동 | 에이전트 | 오디오 전송 → Gemini 응답 → TTS | 텍스트+오디오 응답 | 규칙 (200 + audio) | 재시도(2) |
| 4.3 | 채팅 버블 표시 | 에이전트 | Talk 화면에 user/assistant 버블 | 양방향 버블 렌더링 | 규칙 (빌드) | 재시도(2) |
| 4.4 | 오디오 재생 | 에이전트 | just_audio — 24kHz PCM 재생 | 소리 출력 | 사람 검토 | 에스컬레이션 |
| 4.5 | messages INSERT | 에이전트 | 대화 즉시 SQLite 저장 | SELECT 확인 | 스키마 | 재시도(1) |

---

#### Phase 5: Vertex Live API 실시간 대화 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 5.1 | WS Proxy 구현 | 에이전트 | ws/live_proxy.py — 양방향 오디오 중계 | WS 연결 성공 | 규칙 (WS handshake) | 재시도(2) |
| 5.2 | ContextWindow 주입 | 에이전트 | 세션 시작 시 system instruction 조립 | 프롬프트 주입 확인 | LLM 자기검증 | 재시도(2) |
| 5.3 | 실시간 전사 저장 | 에이전트 | WS 이벤트마다 messages INSERT | 전사 텍스트 저장 | 스키마 (SELECT) | 재시도(1) |
| 5.4 | Barge-in 처리 | 에이전트 | interrupt 메시지 → session reset | 발화 중지 성공 | 사람 검토 | 스킵+로그 |
| 5.5 | Flutter WS 클라이언트 | 에이전트 | web_socket_channel — Talk 화면 연동 | 실시간 음성 대화 | 사람 검토 (데모) | 에스컬레이션 |
| 5.6 | Keepalive 설정 | 스크립트 | 30s ping/pong | 60분 연결 유지 | 규칙 (타임아웃 미발생) | 재시도(1) |

---

#### Phase 6: 캐릭터 라이브러리 `[P1]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 6.1 | MyToys 목록 완성 | 에이전트 | GET /toys → GridView 바인딩 | 복수 캐릭터 표시 | 규칙 (빌드) | 재시도(2) |
| 6.2 | 캐릭터 선택 → Talk | 에이전트 | toyId 전달 → Talk 화면 진입 | 올바른 프롬프트 로드 | LLM 자기검증 | 재시도(2) |
| 6.3 | 캐릭터 삭제 | 에이전트 | 부모 전용 삭제 (owner_uid 검증) | CASCADE 삭제 성공 | 스키마 (SELECT 0행) | 재시도(1) |

---

#### Phase 7: 부모 화면 `[P1]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 7.1 | 날짜별 슬라이드 뷰어 | 에이전트 | GET /logs/{toyId} → PageView | 날짜 스와이프 동작 | 규칙 (빌드) | 재시도(2) |
| 7.2 | 메시지 버블 표시 | 에이전트 | conversations[] → 채팅 UI | 시간+역할+텍스트 표시 | 규칙 (빌드) | 재시도(2) |
| 7.3 | 주간 요약 표시 | 에이전트 | GET /summary/{toyId} → 요약 카드 | summary + topics 표시 | 규칙 (빌드) | 스킵+로그 |

---

#### Phase 8: 성능 최적화 `[P2]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 8.1 | WS 연결 안정성 | 에이전트 | 자동 재연결 (max 3회) + 턴제 fallback | 끊김 시 복구 | 사람 검토 | 스킵+로그 |
| 8.2 | 오디오 버퍼 최적화 | 에이전트 | 100ms 프레임 단위 튜닝 | 레이턴시 < 500ms | 규칙 (측정) | 스킵+로그 |
| 8.3 | Background Tasks | 에이전트 | APScheduler — daily_aggregator + weekly_summarizer | cron 정상 실행 | 규칙 (로그) | 스킵+로그 |

---

#### Phase 9: 해커톤 데모 준비 `[P0]`

| # | Step | 처리 주체 | 작업 | 성공 기준 | 검증 | 실패 |
|---|------|-----------|------|-----------|------|------|
| 9.1 | 데모 데이터 시드 | 스크립트 | SQLite에 toys 2건 + daily_logs 3건 + weekly_summaries 1건 INSERT | 데이터 조회 성공 | 스키마 | 재시도(1) |
| 9.2 | UX 연출 | 에이전트 | 캐릭터 생성 파티클 + bounce 애니메이션 | 애니메이션 재생 | 사람 검토 | 스킵+로그 |
| 9.3 | 기억 시연 시나리오 | 에이전트 | 데모 데이터 기반 ContextWindow 주입 확인 | "어제 무지개" 반응 | LLM 자기검증 | 재시도(2) |
| 9.4 | E2E 데모 리허설 | 사람 | 데모 플로우 7단계 수행 | 전 단계 성공 | 사람 검토 | 에스컬레이션 |

---

### 2.3 분기 조건 & 상태 전이

```
[Phase N 완료?]
    │
    ├─ YES → Phase N+1 시작
    │
    └─ NO ─→ [실패 유형?]
               │
               ├─ 빌드/컴파일 에러 → 자동 재시도 (max 2)
               │     └─ 재시도 실패 → 에스컬레이션
               │
               ├─ API 연동 실패 → 로그 + 다음 Step 진행 (비차단)
               │
               └─ 환경/인프라 문제 → 에스컬레이션 (수동 개입)
```

**핵심 분기:**
- Phase 5 (Live API) 실패 시 → Phase 4 (턴제 대화)로 fallback. 데모는 턴제로 진행
- Phase 3 Stage 3 (이미지 품질) 3회 실패 → 배경 제거 원본 이미지 사용
- Phase 8 전체 → P2이므로 시간 부족 시 전부 스킵 가능

---

## 3. 구현 스펙

### 3.1 폴더 구조 (듀얼 호환)

```
/toystory                              # project-root
├── CLAUDE.md                          # Claude Code 메인 에이전트 지침
├── .agent/
│   ├── rules/
│   │   └── RULES.md                   # Codex 메인 에이전트 지침 (CLAUDE.md 미러)
│   ├── skills/
│   │   ├── flutter-init/              # [기존] Flutter 프로젝트 초기화 (재활용)
│   │   ├── db-setup/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── init_tables.py     # SQLite DDL 실행
│   │   │       └── seed_demo.py       # 데모 데이터 INSERT
│   │   ├── gemini-integration/
│   │   │   ├── SKILL.md
│   │   │   └── references/
│   │   │       ├── image-pipeline.md  # Stage 1/2/3 프롬프트 + 검증 로직
│   │   │       ├── voice-matching.md  # toy.type → voiceProfile 매핑표
│   │   │       └── prompt-layers.md   # 3층 프롬프트 + ContextWindow 템플릿
│   │   ├── api-test/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       └── test_endpoints.sh  # curl 기반 API 스모크 테스트
│   │   └── build-verify/
│   │       ├── SKILL.md
│   │       └── scripts/
│   │           ├── flutter_check.sh   # flutter analyze + build
│   │           └── python_check.sh    # py_compile + uvicorn 기동 테스트
│   └── agents/
│       ├── backend/
│       │   └── AGENT.md               # Backend 서브에이전트 지침
│       └── frontend/
│           └── AGENT.md               # Frontend 서브에이전트 지침
├── .claude/                           # Claude Code 전용 (CLAUDE.md에서 참조)
│   └── settings.json                  # (선택) Claude Code 설정
├── doc/
│   ├── unified-spec.md                # 최종 통합 명세서 v1.1 (복사 배치)
│   ├── api-contract.md                # API 계약서 (FE/BE 공통 참조)
│   ├── be-spec.md                     # 백엔드 명세 (명세서 기반 업데이트)
│   └── fe-spec.md                     # 프론트엔드 명세 (명세서 기반 업데이트)
├── backend/                           # FastAPI 프로젝트
│   ├── main.py
│   ├── routers/
│   ├── ws/
│   ├── middleware/
│   ├── config/
│   ├── db/
│   ├── tasks/
│   ├── uploads/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                          # Flutter 프로젝트 (toytalk_app)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/
│   │   ├── models/
│   │   ├── services/
│   │   ├── providers/
│   │   ├── screens/
│   │   └── widgets/
│   ├── pubspec.yaml
│   └── android/
└── output/                            # 중간 산출물 (Phase별 결과)
    ├── phase0_env_check.log
    ├── phase1_flutter_analyze.log
    ├── phase2_api_test.log
    └── demo_seed_data.sql
```

### 3.2 CLAUDE.md 핵심 섹션 목록

| 섹션 | 내용 |
|------|------|
| **Project Overview** | ToyTalk 서비스 개요 + 기술 스택 요약 |
| **Architecture** | 3-Tier 아키텍처 + 데이터 플로우 요약 |
| **Priority System** | P0/P1/P2 태그 정의 + Phase별 우선순위 |
| **Agent Structure** | 서브에이전트 2개 (backend/frontend) 역할 + 호출 규칙 |
| **Shared Contract** | doc/api-contract.md를 SSOT(Single Source of Truth)로 명시 |
| **Phase Execution** | Phase 0→9 순서 + 각 Phase 완료 기준 |
| **Skill Registry** | 5개 스킬 이름 + 트리거 조건 |
| **Quality Gates** | flutter analyze 0 error / API 스모크 테스트 통과 / 데모 리허설 |
| **Constraints** | 명세서 §6 통합 제약조건 35개 참조 링크 |

### 3.3 에이전트 구조

```
┌─────────────────────────────────────────────┐
│  MAIN ORCHESTRATOR                          │
│  (CLAUDE.md / RULES.md)                     │
│                                             │
│  역할: Phase 순서 제어, 서브에이전트 호출,  │
│        우선순위 판단, doc/ 참조 라우팅       │
│                                             │
│  ┌──────────┐  ┌──────────┐                 │
│  │ backend  │  │ frontend │                 │
│  │  agent   │  │  agent   │                 │
│  └────┬─────┘  └────┬─────┘                 │
│       │              │                      │
│  Skills (공유):                              │
│  db-setup, gemini-integration,              │
│  api-test, build-verify, flutter-init       │
└─────────────────────────────────────────────┘
```

**서브에이전트 분리 근거:**
- Frontend(Dart/Flutter)와 Backend(Python/FastAPI)는 언어·프레임워크·도메인 지식이 완전히 상이
- 각 에이전트의 컨텍스트 윈도우에 불필요한 지식 로드를 방지 (Dart 문법 ↔ Python 문법)
- 독립적으로 빌드/검증 가능한 단위

### 3.4 서브에이전트 정의

#### backend-agent

| 항목 | 내용 |
|------|------|
| **이름** | backend |
| **파일** | `.agent/agents/backend/AGENT.md` |
| **역할** | FastAPI 서버, SQLite CRUD, WS Proxy, Gemini API 호출, Background Tasks, Safety Filter |
| **트리거** | Phase 0.4~0.5, Phase 2 전체, Phase 3 전체, Phase 4.2/4.5, Phase 5.1~5.3/5.6, Phase 8.3 |
| **입력** | doc/unified-spec.md (§2~§S5), doc/api-contract.md, doc/be-spec.md |
| **출력** | backend/ 디렉토리 전체 (실행 가능한 FastAPI 서버) |
| **참조 스킬** | db-setup, gemini-integration, api-test, build-verify |
| **데이터 전달** | 완성된 API 엔드포인트 URL을 doc/api-contract.md에 기록 → frontend-agent가 참조 |

#### frontend-agent

| 항목 | 내용 |
|------|------|
| **이름** | frontend |
| **파일** | `.agent/agents/frontend/AGENT.md` |
| **역할** | Flutter 4화면, Audio I/O, WebSocket 클라이언트, 상태 관리, UX 연출 |
| **트리거** | Phase 0.1~0.3/0.6, Phase 1 전체, Phase 4.1/4.3/4.4, Phase 5.4~5.5, Phase 6 전체, Phase 7 전체, Phase 9.2 |
| **입력** | doc/unified-spec.md (§2~§S5), doc/api-contract.md, doc/fe-spec.md |
| **출력** | frontend/ 디렉토리 전체 (빌드 가능한 Flutter 앱) |
| **참조 스킬** | flutter-init, build-verify |
| **데이터 전달** | api-contract.md의 엔드포인트 정의를 기반으로 서비스 레이어 구현 |

### 3.5 스킬 정의

| 스킬명 | 역할 | 트리거 조건 | 참조 에이전트 |
|--------|------|-------------|---------------|
| **flutter-init** | Flutter 프로젝트 생성 + 패키지 설치 + 폴더 구조 | Phase 0.2~0.3 | frontend |
| **db-setup** | SQLite DDL 실행 + 데모 데이터 시드 | Phase 0.5, Phase 9.1 | backend |
| **gemini-integration** | Gemini API 호출 패턴, 프롬프트 템플릿, 음성 매칭 참조 | Phase 3 전체, Phase 4.2, Phase 5.2, Phase 8.3 | backend |
| **api-test** | curl 기반 엔드포인트 스모크 테스트 | Phase 2.10, Phase 4 완료 후, Phase 5 완료 후 | backend |
| **build-verify** | flutter analyze + python 컴파일 + 빌드 검증 | 매 Phase 완료 시 | 양쪽 |

### 3.6 작업 단계별 처리 방식

| 작업 유형 | 처리 주체 | 예시 |
|-----------|-----------|------|
| **프롬프트 설계/조립** | 에이전트 판단 | 3층 프롬프트 변수 치환, ContextWindow 조립 로직 |
| **API 라우터 코드 작성** | 에이전트 판단 | FastAPI 라우터 + Pydantic 스키마 |
| **Flutter 화면 코드** | 에이전트 판단 | 위젯 트리 설계, 상태 관리 패턴 |
| **Gemini API 호출 코드** | 에이전트 판단 | SDK 사용법 + 에러 핸들링 |
| **DDL 실행** | 스크립트 | scripts/init_tables.py |
| **데모 데이터 시드** | 스크립트 | scripts/seed_demo.py |
| **빌드 검증** | 스크립트 | scripts/flutter_check.sh, python_check.sh |
| **API 스모크 테스트** | 스크립트 | scripts/test_endpoints.sh |
| **이미지 품질 검증** | 에이전트 판단 | Stage 3 색상/특징 비교 로직 설계 |
| **안전 필터 규칙** | 에이전트 판단 | 키워드 목록 + 패턴 매칭 로직 |

### 3.7 데이터 전달 패턴

| 전달 경로 | 방식 | 파일 |
|-----------|------|------|
| Main → Backend | 파일 기반 | doc/unified-spec.md, doc/api-contract.md |
| Main → Frontend | 파일 기반 | doc/unified-spec.md, doc/api-contract.md |
| Backend → Frontend | 파일 기반 | doc/api-contract.md (SSOT — Backend가 엔드포인트 확정 → Frontend가 참조) |
| Phase N → Phase N+1 | 파일 기반 | output/phaseN_result.log (완료 상태 + 검증 결과) |
| 스킬 스크립트 결과 | stdout + 파일 | exit code + output/*.log |

### 3.8 주요 산출물 파일 형식

| 산출물 | 형식 | 위치 |
|--------|------|------|
| FastAPI 서버 코드 | .py | backend/ |
| Flutter 앱 코드 | .dart | frontend/lib/ |
| SQLite DDL | .sql / .py | .agent/skills/db-setup/scripts/ |
| 데모 시드 데이터 | .py (INSERT 스크립트) | .agent/skills/db-setup/scripts/ |
| API 테스트 | .sh (curl) | .agent/skills/api-test/scripts/ |
| Docker 이미지 | Dockerfile | backend/ |
| 검증 로그 | .log | output/ |
| API 계약서 | .md | doc/api-contract.md |

---

## 4. 실행 순서 요약 (해커톤 1일 타임라인)

```
[T+0h]  Phase 0: 환경 준비 ────────────── P0 (30분)
[T+0.5h] Phase 2: 백엔드 뼈대 ─────────── P0 (2시간)
         ↕ (병렬 가능)
[T+0.5h] Phase 1: Flutter 앱 뼈대 ──────── P0 (2시간)
[T+2.5h] Phase 3: 캐릭터 이미지 생성 ───── P0 (1.5시간)
[T+4h]  Phase 4: 턴제 대화 ─────────────── P0 (1시간)
[T+5h]  Phase 5: Live API 실시간 대화 ──── P0 (2시간)
[T+7h]  Phase 9: 데모 준비 + 시드 데이터 ── P0 (30분)
─── P0 완료 라인 (8시간) ───
[T+7.5h] Phase 6: 캐릭터 라이브러리 ────── P1 (30분)
[T+8h]  Phase 7: 부모 화면 ─────────────── P1 (1시간)
[T+9h]  Phase 8: 최적화 ────────────────── P2 (여유 시)
```

**핵심:** Phase 1(FE)과 Phase 2(BE)는 **병렬 실행 가능** — api-contract.md를 먼저 확정하고 양쪽이 독립 개발.

---

## 5. 듀얼 호환 전략

### Claude Code (.claude/) 사용 시

```
CLAUDE.md → 메인 오케스트레이터
  ├── 서브에이전트 호출: .agent/agents/backend/AGENT.md 읽기 → 실행
  ├── 서브에이전트 호출: .agent/agents/frontend/AGENT.md 읽기 → 실행
  └── 스킬 참조: .agent/skills/*/SKILL.md 읽기 → scripts/ 실행
```

### Codex (.agent/) 사용 시

```
.agent/rules/RULES.md → 메인 오케스트레이터 (CLAUDE.md와 동일 내용)
  ├── 서브에이전트: .agent/agents/backend/AGENT.md
  ├── 서브에이전트: .agent/agents/frontend/AGENT.md
  └── 스킬: .agent/skills/*/SKILL.md
```

### 호환 규칙

| 규칙 | 설명 |
|------|------|
| **CLAUDE.md = RULES.md** | 두 파일은 내용을 동기화. CLAUDE.md가 원본, RULES.md는 미러 |
| **에이전트/스킬 위치** | 모두 `.agent/` 하위에 배치 (Claude Code도 이 경로 참조) |
| **doc/ 공유** | 양쪽 모두 doc/ 디렉토리를 SSOT으로 참조 |
| **output/ 공유** | Phase 결과물은 output/에 저장, 양쪽 모두 접근 |

---

## 6. 기존 스킬 처리

### 유지 (재활용)

| 스킬 | 사유 |
|------|------|
| **flutter-init** | Flutter 프로젝트 초기화에 직접 활용 (Phase 0) |

### 제거 또는 비활성

| 스킬 | 사유 |
|------|------|
| card-news-generator (v1, v2) | ToyTalk 무관 |
| code-prompt-coach | ToyTalk 무관 |
| codex, codex-claude-loop, codex-claude-cursor-loop | 범용 도구, ToyTalk 전용으로 대체 |
| landing-page-guide (v1, v2) | ToyTalk 무관 |
| nextjs15-init | Next.js 무관 (Flutter 사용) |
| design-prompt-generator-v2 | ToyTalk 전용 gemini-integration으로 대체 |
| meta-prompt-generator | 범용, 필요 시 참조만 |
| prompt-enhancer | 범용, gemini-integration에 흡수 |
| web-search | 범용, 필요 시 참조만 |
| web-to-markdown | ToyTalk 무관 |
| workthrough (v1, v2) | ToyTalk 무관 |
| midjourney-cardnews-bg | ToyTalk 무관 |
| frontend-design | gemini-integration + flutter AGENT.md에 흡수 |
| code-changelog | 해커톤에서 불필요 |
| gemini-logo-remover | ToyTalk 무관 |

> **처리 방식:** 제거하지 않고 `.agent/skills/_archive/`로 이동하여 비활성화.
> ToyTalk 전용 5개 스킬만 활성 상태로 유지.

---

*End of Agent System Design*
