<!-- This file is a mirror of /CLAUDE.md for Codex compatibility. Keep in sync. -->
# ToyTalk — Main Orchestrator

> 이 파일은 Claude Code / Codex 메인 에이전트 지침입니다.
> `.agent/rules/RULES.md`와 동일 내용을 유지합니다 (CLAUDE.md가 원본).

---

## 1. Project Overview

**ToyTalk**은 4~7세 어린이가 자신의 장난감을 AI 캐릭터로 변환하고 음성 대화하는 서비스다.

| 항목 | 값 |
|------|-----|
| **Target** | Google Gemini 3 해커톤 (1일 스프린트) |
| **Frontend** | Flutter 3.41 / Dart 3.11 (Android 에뮬레이터 데모) |
| **Backend** | Python 3.12 + FastAPI + Uvicorn |
| **DB** | SQLite (aiosqlite) — 5 테이블 |
| **AI** | Vertex AI — Gemini Vision, ImageGen, Live API, TTS, Flash |
| **Deploy** | Docker → Cloud Run (asia-northeast3, single instance) |
| **Budget** | Vertex AI $5 이내 |

---

## 2. Architecture

```
Flutter Client ─── HTTP (REST) ──→ FastAPI Backend ──→ Vertex AI
                └── WebSocket ──→ WS Proxy ──────→ Live API
                                        ↓
                                    SQLite + Local FS
```

**3-Tier:** Presentation (Flutter) → Application (FastAPI) → AI/Data (Vertex + SQLite)

**4 화면:** MyToys (GridView) | CreateToy (Camera) | Talk (Voice Chat) | Parent (Logs/Slides)

**7 REST 엔드포인트:** POST /toys, GET /toys, GET /toys/{id}, POST /talk, POST /tts, GET /logs/{id}, GET /summary/{id}

**1 WebSocket:** /ws/live (Vertex Live API 양방향 프록시)

---

## 3. Priority System

| Tag | 의미 | Phase |
|-----|------|-------|
| **P0** | 데모 필수 (없으면 데모 불가) | 0, 1, 2, 3, 4, 5, 9 |
| **P1** | 임팩트 강화 (심사 점수 상승) | 6, 7 |
| **P2** | 완성도 (프로덕션 대비) | 8 |

**P0를 모두 완료한 후에만 P1 진행. P1 완료 후 여유가 있을 때만 P2 진행.**

---

## 4. Agent Structure

```
┌───────────────────────────────────────┐
│  THIS FILE — MAIN ORCHESTRATOR        │
│  역할: Phase 순서 제어, 서브에이전트   │
│        호출, 우선순위 판단             │
│                                       │
│   ┌────────────┐  ┌────────────┐      │
│   │  backend   │  │  frontend  │      │
│   │  agent     │  │  agent     │      │
│   └─────┬──────┘  └─────┬──────┘      │
│         │                │             │
│  Shared Skills:                       │
│  db-setup · gemini-integration ·      │
│  api-test · build-verify · flutter-init│
└───────────────────────────────────────┘
```

### 서브에이전트 호출 규칙

1. **서브에이전트 간 직접 호출 금지** — 반드시 이 오케스트레이터를 통해 조율
2. **Phase 순서를 준수** — 선행 Phase 완료 확인 후 다음 Phase 진행
3. **병렬 허용:** Phase 1(FE)과 Phase 2(BE)는 api-contract.md 확정 후 병렬 실행 가능
4. **서브에이전트 호출 시** 해당 AGENT.md를 읽고, 필요한 스킬의 SKILL.md를 참조
5. **Phase 완료 시** 반드시 build-verify 스킬 실행 → output/phaseN_result.log 기록

### 서브에이전트 파일 위치

| Agent | File | 담당 Phase |
|-------|------|-----------|
| **backend** | `.agent/agents/backend/AGENT.md` | 0.4~0.5, 2.*, 3.*, 4.2/4.5, 5.1~5.3/5.6, 8.3, 9.1 |
| **frontend** | `.agent/agents/frontend/AGENT.md` | 0.1~0.3/0.6, 1.*, 4.1/4.3/4.4, 5.4~5.5, 6.*, 7.*, 9.2 |

---

## 5. Shared Contract (SSOT)

| Document | Role | 위치 |
|----------|------|------|
| **api-contract.md** | FE/BE 공통 API 계약서. **양쪽 모두 이 파일을 기준으로 개발** | `doc/api-contract.md` |
| **unified-spec.md** | 최종 통합 명세서 v1.1 (도메인 지식 + 제약조건 전체) | `doc/unified-spec.md` |
| **be-spec.md** | Backend 구현 상세 (BE agent 전용 참조) | `doc/be-spec.md` |
| **fe-spec.md** | Frontend 구현 상세 (FE agent 전용 참조) | `doc/fe-spec.md` |

**api-contract.md 업데이트 흐름:**
1. Backend agent가 엔드포인트 구현 완료 시 api-contract.md에 실제 스키마 반영
2. Frontend agent는 항상 api-contract.md의 최신 버전을 기준으로 서비스 레이어 작성

---

## 6. Phase Execution Order

```
[T+0h]   Phase 0: 환경 준비 ─────────────── P0 (30분)
[T+0.5h] Phase 1: Flutter 앱 뼈대 ────────── P0 (2시간)  ← 병렬
         Phase 2: 백엔드 뼈대 ──────────── P0 (2시간)  ← 병렬
[T+2.5h] Phase 3: 캐릭터 이미지 생성 ──────── P0 (1.5시간)
[T+4h]   Phase 4: 턴제 대화 ─────────────── P0 (1시간)
[T+5h]   Phase 5: Live API 실시간 대화 ───── P0 (2시간)
[T+7h]   Phase 9: 데모 준비 + 시드 데이터 ── P0 (30분)
──── P0 완료 라인 (8시간) ────
[T+7.5h] Phase 6: 캐릭터 라이브러리 ──────── P1 (30분)
[T+8h]   Phase 7: 부모 화면 ─────────────── P1 (1시간)
[T+9h]   Phase 8: 최적화 ───────────────── P2 (여유 시)
```

### Phase별 완료 기준

| Phase | 완료 기준 | 검증 명령 |
|-------|-----------|-----------|
| 0 | 5개 테이블 생성, 의존성 resolve, 디바이스 1개 이상 | `flutter devices`, `sqlite3 .tables` |
| 1 | flutter analyze 0 error, 4화면 전환 성공 | `flutter analyze` |
| 2 | 5개 엔드포인트 200/201 응답, docker build 성공 | api-test 스킬 실행 |
| 3 | 사진→아바타 E2E 성공, voiceProfile INSERT 완료 | curl POST /toys + DB 확인 |
| 4 | 양방향 음성 대화 동작 (녹음→응답→재생) | 수동 테스트 |
| 5 | 실시간 음성 대화 + 60분 연결 유지 | WS 연결 테스트 |
| 6 | 복수 캐릭터 표시 + 선택→Talk 진입 | 빌드 성공 |
| 7 | 날짜별 슬라이드 스와이프 + 요약 카드 | 빌드 성공 |
| 8 | WS 자동 재연결 + Background Tasks 동작 | 로그 확인 |
| 9 | 7단계 데모 플로우 리허설 성공 | 수동 E2E |

---

## 7. Skill Registry

| Skill | Location | Trigger | Agent |
|-------|----------|---------|-------|
| **flutter-init** | `.agent/skills/flutter-init/SKILL.md` | Phase 0.2~0.3 | frontend |
| **db-setup** | `.agent/skills/db-setup/SKILL.md` | Phase 0.5, 9.1 | backend |
| **gemini-integration** | `.agent/skills/gemini-integration/SKILL.md` | Phase 3.*, 4.2, 5.2, 8.3 | backend |
| **api-test** | `.agent/skills/api-test/SKILL.md` | Phase 2.10, 4 완료, 5 완료 | backend |
| **build-verify** | `.agent/skills/build-verify/SKILL.md` | 매 Phase 완료 시 | both |

### 스킬 호출 패턴
```
1. SKILL.md 읽기 (역할, 입출력, 참조 문서 확인)
2. scripts/ 내 해당 스크립트 실행
3. exit code + stdout 확인
4. 실패 시 SKILL.md의 실패 처리 지침 따름
```

---

## 8. Quality Gates

모든 Phase 완료 시 아래 게이트를 통과해야 다음 Phase 진행:

| Gate | 명령 | 통과 기준 |
|------|------|-----------|
| **Flutter 정적 분석** | `cd frontend && flutter analyze` | 0 errors |
| **Python 컴파일** | `cd backend && python -m py_compile main.py` | exit 0 |
| **API 스모크 테스트** | `.agent/skills/api-test/scripts/test_endpoints.sh` | 5개 200/201 |
| **데모 리허설** | 7단계 플로우 수동 확인 (Phase 9) | 전체 통과 |

---

## 9. Constraints Reference

모든 제약조건은 `doc/unified-spec.md` §6 통합 제약조건 레지스트리에 정의됨.
총 35개 제약조건 (C-IMG-*, C-VOC-*, C-PRO-*, C-PAR-*, C-MEM-*, C-LAT-*, C-ERR-*, C-VAD-*).

**에이전트는 코드 구현 시 해당 도메인의 제약조건을 반드시 확인하고 준수할 것.**

---

## 10. Error Escalation

| 상황 | 처리 |
|------|------|
| 빌드/컴파일 에러 | 자동 재시도 (max 2) → 실패 시 에러 로그 출력 + 사용자에게 확인 요청 |
| API 연동 실패 | 로그 기록 + 다음 Step 진행 (비차단) |
| Vertex API quota 초과 | 캐시 응답 사용 + 로그 경고 |
| 환경/인프라 문제 | 즉시 사용자에게 에스컬레이션 |

---

## 11. File Structure

```
/toystory
├── CLAUDE.md                              ← 이 파일
├── .agent/
│   ├── rules/RULES.md                     # CLAUDE.md 미러 (Codex 호환)
│   ├── skills/
│   │   ├── flutter-init/SKILL.md          # Flutter 프로젝트 초기화
│   │   ├── db-setup/SKILL.md              # SQLite DDL + 시드
│   │   ├── gemini-integration/SKILL.md    # Gemini API 패턴 + 프롬프트
│   │   ├── api-test/SKILL.md              # curl 스모크 테스트
│   │   └── build-verify/SKILL.md          # 빌드 검증
│   └── agents/
│       ├── backend/AGENT.md               # Backend 서브에이전트
│       └── frontend/AGENT.md              # Frontend 서브에이전트
├── doc/
│   ├── unified-spec.md                    # 최종 통합 명세서 v1.1
│   ├── api-contract.md                    # SSOT (FE/BE 공통)
│   ├── be-spec.md                         # Backend 구현 상세
│   └── fe-spec.md                         # Frontend 구현 상세
├── backend/                               # FastAPI 서버
│   ├── main.py
│   ├── routers/ (toys.py, talk.py, tts.py, logs.py, auth.py)
│   ├── ws/live_proxy.py
│   ├── middleware/ (auth.py, safety.py)
│   ├── config/prompts.py
│   ├── db/database.py
│   ├── tasks/scheduler.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                              # Flutter 앱
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/
│   │   ├── services/
│   │   ├── screens/ (my_toys, create_toy, talk, parent)
│   │   ├── widgets/
│   │   └── providers/
│   ├── pubspec.yaml
│   └── android/
└── output/                                # Phase별 검증 로그
```

---

*End of CLAUDE.md*
