# Frontend Agent

> Flutter 앱 전담 서브에이전트
> 호출: CLAUDE.md (메인 오케스트레이터)에서만 트리거

---

## 1. Identity

| 항목 | 값 |
|------|-----|
| **이름** | frontend |
| **언어** | Dart 3.11 |
| **프레임워크** | Flutter 3.41 |
| **플랫폼** | Android (에뮬레이터 데모) |
| **상태 관리** | Provider (기본) / Riverpod (선택) |
| **작업 디렉토리** | `frontend/` |

---

## 2. Responsibilities

| 영역 | 구현 내용 |
|------|-----------|
| **4 화면** | MyToys (GridView), CreateToy (Camera/Gallery), Talk (Voice Chat), Parent (Logs/Slides) |
| **Audio I/O** | flutter_sound (녹음: PCM 16kHz/16bit/mono), just_audio (재생: 24kHz) |
| **WebSocket** | web_socket_channel — /ws/live 연결, 오디오 프레임 스트리밍, Barge-in |
| **REST Client** | http 패키지 — api-contract.md 기반 서비스 레이어 |
| **상태 관리** | Provider — 장난감 목록, 대화 세션, 인증 상태 |
| **UX 연출** | 캐릭터 생성 파티클 + bounce 애니메이션 (Phase 9 데모 임팩트) |
| **Parent View** | 날짜별 대화 슬라이드 뷰어 (PageView + swipe) |

---

## 3. Trigger Phases

| Phase | Steps | 작업 |
|-------|-------|------|
| **0** | 0.1~0.3, 0.6 | Flutter 환경 확인 + 프로젝트 생성 + 패키지 설치 + 에뮬레이터 확인 |
| **1** | 1.1~1.9 | Flutter MVP 전체 (폴더구조, 모델, API서비스, 4화면, 라우팅, 검증) |
| **4** | 4.1, 4.3, 4.4 | 오디오 녹음 + 채팅 버블 + 오디오 재생 |
| **5** | 5.4~5.5 | Barge-in 처리 + Flutter WS 클라이언트 |
| **6** | 6.1~6.3 | 캐릭터 라이브러리 완성 (목록, 선택→Talk, 삭제) |
| **7** | 7.1~7.3 | 부모 화면 (슬라이드, 메시지 버블, 주간 요약) |
| **9** | 9.2 | UX 연출 (파티클 + bounce 애니메이션) |

---

## 4. Input / Output

| 방향 | 내용 |
|------|------|
| **Input** | `doc/unified-spec.md` (§S1.3 UX 연출, §S3 대화 프롬프트), `doc/api-contract.md`, `doc/fe-spec.md` |
| **Output** | `frontend/` 디렉토리 전체 — 빌드 가능한 Flutter 앱 |
| **SSOT 참조** | `doc/api-contract.md`의 엔드포인트/스키마 기반으로 서비스 레이어 구현 |

---

## 5. Referenced Skills

| Skill | 용도 | 트리거 |
|-------|------|--------|
| **flutter-init** | Flutter 프로젝트 생성 + 패키지 설치 + 폴더 구조 | Phase 0.2~0.3 |
| **build-verify** | flutter analyze + debug build 검증 | 매 Phase 완료 시 |

---

## 6. Frontend File Structure

```
frontend/
├── pubspec.yaml              # 의존성 정의
├── android/                  # Android 플랫폼 설정
│
└── lib/
    ├── main.dart             # 앱 진입점 + MaterialApp + 라우팅
    │
    ├── models/               # 데이터 모델 (api-contract.md 기반)
    │   ├── toy.dart          # Toy — toyId, toyName, avatarUrl, voiceProfile, childName...
    │   ├── session.dart      # Session — sessionId, toyId, createdAt, lastMessageAt
    │   ├── message.dart      # Message — messageId, role, text, audioUrl, createdAt
    │   ├── daily_log.dart    # DailyLog — date, conversations[], totalMessages
    │   ├── weekly_summary.dart # WeeklySummary — weekId, summary, topics, emotions
    │   └── user.dart         # User — userId, email, nickname, tokens
    │
    ├── services/             # API 통신 레이어 (api-contract.md SSOT)
    │   ├── api_client.dart   # Base HTTP client (baseUrl, headers, error handling)
    │   ├── auth_service.dart # POST /auth/signup, /login → JWT 저장
    │   ├── toy_service.dart  # POST/GET/DELETE /toys
    │   ├── talk_service.dart # POST /talk (턴제)
    │   ├── tts_service.dart  # POST /tts
    │   ├── log_service.dart  # GET /logs/{toyId}, GET /summary/{toyId}
    │   └── ws_service.dart   # WebSocket /ws/live — 연결, 오디오 스트리밍, Barge-in
    │
    ├── providers/            # 상태 관리
    │   ├── auth_provider.dart    # 인증 상태 (로그인/로그아웃, 토큰)
    │   ├── toy_provider.dart     # 장난감 목록 + CRUD 상태
    │   ├── talk_provider.dart    # 대화 세션 상태 (메시지 목록, 녹음 중 여부)
    │   └── parent_provider.dart  # 부모 화면 상태 (dailyLogs, weeklySummary)
    │
    ├── screens/              # 4개 메인 화면
    │   ├── my_toys/
    │   │   └── my_toys_screen.dart   # GridView + ToyCard. 탭→Talk, 길게 누르기→삭제
    │   ├── create_toy/
    │   │   └── create_toy_screen.dart # Camera/Gallery → 이미지 선택 → API 업로드 → 결과
    │   ├── talk/
    │   │   └── talk_screen.dart       # 채팅 버블 + 녹음 버튼 + 오디오 재생
    │   │                               # WS 모드: 실시간 스트리밍
    │   │                               # 턴제 모드: 녹음→전송→응답→재생
    │   └── parent/
    │       └── parent_screen.dart     # PageView (날짜별 슬라이드) + 주간 요약 카드
    │
    └── widgets/              # 재사용 위젯
        ├── toy_card.dart     # 캐릭터 카드 (아바타 + 이름)
        ├── chat_bubble.dart  # 대화 버블 (user: 오른쪽, assistant: 왼쪽)
        ├── record_button.dart # 녹음 버튼 (탭&홀드 or 토글)
        ├── magic_animation.dart # ✨ 캐릭터 생성 파티클 + dissolve + bounce
        └── date_slider.dart  # 부모 화면 날짜 dot indicator
```

---

## 7. Key Implementation Patterns

### 7.1 API Client Base

```dart
// services/api_client.dart
class ApiClient {
  static const baseUrl = 'http://localhost:8000/api/v1'; // → 배포 시 변경
  String? _accessToken;

  Future<Map<String, String>> get _headers => {
    'Content-Type': 'application/json',
    if (_accessToken != null) 'Authorization': 'Bearer $_accessToken',
  };

  // GET, POST, DELETE 공통 메서드
  // 에러 시 {"success": false, "error": {...}} 파싱
}
```

### 7.2 WebSocket 연결 패턴

```dart
// services/ws_service.dart
class WsService {
  WebSocketChannel? _channel;

  void connect(String toyId, String sessionId) {
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://localhost:8000/ws/live?toyId=$toyId&sessionId=$sessionId'),
    );
  }

  void sendAudioFrame(Uint8List pcmFrame) {
    // Binary frame으로 전송 (JSON wrapper X — overhead 제거)
    _channel?.sink.add(pcmFrame);
  }

  void sendInterrupt() {
    // Barge-in: JSON text frame
    _channel?.sink.add(jsonEncode({'type': 'interrupt'}));
  }

  Stream<dynamic> get stream => _channel!.stream;
  // binary → 오디오 재생
  // text → 전사 텍스트 → 채팅 버블
}
```

### 7.3 오디오 녹음/재생

```dart
// 녹음: flutter_sound
FlutterSoundRecorder recorder;
await recorder.startRecorder(
  codec: Codec.pcm16,
  sampleRate: 16000,    // 16kHz
  numChannels: 1,       // mono
  // → 100ms 단위 (1600 samples per frame)
);

// 재생: just_audio
AudioPlayer player;
// 24kHz PCM → AudioSource.uri 또는 StreamAudioSource
```

### 7.4 캐릭터 생성 UX 연출 (데모 임팩트)

```dart
// widgets/magic_animation.dart
// Step 1: 사진 업로드
// Step 2: ✨ 파티클 애니메이션 + "마법을 부리고 있어요..." 텍스트
// Step 3: 사진 dissolve 트랜지션 (FadeTransition + ColorFilter)
// Step 4: 캐릭터 pop! (ScaleTransition — bounceOut curve)
// Step 5: TTS "안녕! 나는 {toyName}이야!" 자동 재생
```

### 7.5 부모 화면 슬라이드

```dart
// screens/parent/parent_screen.dart
PageView.builder(
  itemCount: dailyLogs.length,
  itemBuilder: (ctx, i) => DailyLogSlide(
    date: dailyLogs[i].date,
    conversations: dailyLogs[i].conversations,
    // 날짜 헤더 + 메시지 버블 (시간+역할+텍스트)
  ),
)
// + dot indicator (PageController.page)
```

---

## 8. Model Classes Quick Reference

| Model | 주요 필드 | api-contract 연동 |
|-------|-----------|-------------------|
| **Toy** | toyId, toyName, avatarUrl, voiceProfile(Map), childName, type, createdAt | GET/POST /toys |
| **Session** | sessionId, toyId, createdAt, lastMessageAt, messageCount | 내부 관리 |
| **Message** | messageId, role, text, audioUrl, createdAt | GET /logs (conversations) |
| **DailyLog** | date, toyId, totalMessages, conversations(List<Map>), isSummarized | GET /logs/{toyId} |
| **WeeklySummary** | weekId, toyId, summary, topics, emotions, memorableEvents | GET /summary/{toyId} |
| **User** | userId, email, nickname, accessToken, refreshToken | POST /auth/* |

모든 모델은 `fromJson(Map)` + `toJson()` 팩토리 메서드 필수.

---

## 9. Navigation / Routing

```dart
// main.dart — MaterialApp routes
'/' → MyToysScreen         // 기본 화면 (캐릭터 목록)
'/create' → CreateToyScreen // 장난감 촬영 → 캐릭터 생성
'/talk/:toyId' → TalkScreen // 음성 대화
'/parent' → ParentScreen    // 부모 대화 기록
'/login' → LoginScreen      // 부모 로그인
```

화면 전환 규칙:
- MyToys → 캐릭터 탭 → Talk (toyId 전달)
- MyToys → FAB(+) → CreateToy → 완료 → MyToys (새 캐릭터 추가)
- MyToys → 부모 아이콘 → Parent (인증 필요)
- CreateToy → 생성 성공 → magic_animation → MyToys

---

## 10. Flutter Dependencies (pubspec.yaml)

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0
  web_socket_channel: ^2.4.0
  flutter_sound: ^9.2.0
  just_audio: ^0.9.0
  provider: ^6.1.0
  image_picker: ^1.0.0
  path_provider: ^2.1.0
  uuid: ^4.0.0
  shared_preferences: ^2.2.0    # JWT 로컬 저장
```

---

## 11. Constraints Checklist

이 에이전트가 코드 작성 시 반드시 확인할 제약조건:

| ID | 제약 |
|----|------|
| C-IMG-3 | 아바타 생성 후 아이가 즉시 알아볼 수 있어야 함 (UX 연출) |
| C-PRO-2 | 프롬프트는 사용자에게 노출되지 않아야 함 |
| C-LAT-1 | 아바타 생성 전체 <8s (UI 애니메이션으로 대기 분산) |
| C-LAT-2 | Barge-in 반응 <500ms (클라이언트 즉시 interrupt) |
| C-MEM-8 | 부모 뷰: 날짜별 슬라이드 + swipe navigation |
| C-MEM-9 | 슬라이드: date_header + message_bubbles + timestamps + dot_indicator |
| C4 | Audio input: PCM 16bit, 16kHz, mono |
| C5 | Audio output: 24kHz |

---

## 12. Error Handling (Client Side)

| 에러 | 대응 |
|------|------|
| API 통신 실패 | SnackBar "연결에 실패했어요. 다시 시도해주세요" + 재시도 버튼 |
| WS 끊김 | 3초 후 자동 재연결 (max 3) → 실패 시 Talk 화면에 "다시 연결 중..." 표시 → 턴제 모드 fallback |
| 녹음 권한 거부 | 권한 요청 다이얼로그 → 설정으로 이동 안내 |
| 이미지 로드 실패 | placeholder 아바타 표시 |
| JWT 만료 | refresh 시도 → 실패 시 로그인 화면 이동 |

---

*End of Frontend AGENT.md*