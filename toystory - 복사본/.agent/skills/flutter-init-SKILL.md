# Skill: flutter-init

> Flutter 프로젝트 생성 + 패키지 설치 + Clean Architecture 폴더 구조

---

## Purpose

Phase 0에서 Flutter 프로젝트를 빠르게 부트스트랩.
패키지 의존성, 폴더 구조, 기본 설정을 한번에 완료.

## Trigger

| Phase | 용도 |
|-------|------|
| **0.2** | Flutter 프로젝트 생성 |
| **0.3** | 패키지 설치 + 폴더 구조 생성 |

## Referenced By

- frontend agent

## Scripts

| Script | 용도 |
|--------|------|
| `scripts/create_project.sh` | 프로젝트 생성 + 패키지 + 디렉토리 |

## Success Criteria

| 검증 | 명령 | 기대 |
|------|------|------|
| 프로젝트 존재 | `ls frontend/pubspec.yaml` | 파일 존재 |
| 의존성 resolve | `cd frontend && flutter pub get` | exit 0 |
| 폴더 구조 | `ls frontend/lib/screens/` | 4개 디렉토리 존재 |

## Failure Handling

- `flutter create` 실패 → 자동 재시도 1회 → 에스컬레이션
- `flutter pub get` 실패 → pubspec.yaml 오타 확인 → 자동 재시도 2회

---

## Script Specification

```bash
#!/bin/bash
# scripts/create_project.sh
# Flutter 프로젝트 생성 + 패키지 설치 + 폴더 구조

set -e

PROJECT_DIR="frontend"

# 1. 프로젝트 생성 (이미 존재하면 스킵)
if [ ! -f "$PROJECT_DIR/pubspec.yaml" ]; then
  echo "=== Creating Flutter Project ==="
  flutter create --platforms android,ios --project-name toytalk_app "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# 2. 패키지 설치
echo "=== Installing Packages ==="
flutter pub add \
  http \
  web_socket_channel \
  flutter_sound \
  just_audio \
  provider \
  image_picker \
  path_provider \
  uuid \
  shared_preferences

flutter pub get

# 3. Clean Architecture 폴더 구조 생성
echo "=== Creating Directory Structure ==="
mkdir -p lib/models
mkdir -p lib/services
mkdir -p lib/providers
mkdir -p lib/screens/my_toys
mkdir -p lib/screens/create_toy
mkdir -p lib/screens/talk
mkdir -p lib/screens/parent
mkdir -p lib/widgets

# 4. 빈 파일 생성 (placeholder)
touch lib/models/.gitkeep
touch lib/services/.gitkeep
touch lib/providers/.gitkeep
touch lib/widgets/.gitkeep

echo "✅ Flutter project initialized successfully"
echo "   Directory: $PROJECT_DIR"
echo "   Packages: $(grep -c "^  " pubspec.yaml) dependencies"
```

---

## pubspec.yaml Dependencies Reference

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.0                    # REST API 호출
  web_socket_channel: ^2.4.0      # WebSocket (Live API)
  flutter_sound: ^9.2.0           # 오디오 녹음 (PCM 16kHz/16bit/mono)
  just_audio: ^0.9.0              # 오디오 재생 (24kHz)
  provider: ^6.1.0                # 상태 관리
  image_picker: ^1.0.0            # 카메라/갤러리 이미지 선택
  path_provider: ^2.1.0           # 로컬 파일 경로
  uuid: ^4.0.0                    # 고유 ID 생성
  shared_preferences: ^2.2.0      # JWT 로컬 저장
```

## Directory Structure After Init

```
frontend/lib/
├── main.dart
├── models/
│   ├── toy.dart
│   ├── session.dart
│   ├── message.dart
│   ├── daily_log.dart
│   ├── weekly_summary.dart
│   └── user.dart
├── services/
│   ├── api_client.dart
│   ├── auth_service.dart
│   ├── toy_service.dart
│   ├── talk_service.dart
│   ├── tts_service.dart
│   ├── log_service.dart
│   └── ws_service.dart
├── providers/
│   ├── auth_provider.dart
│   ├── toy_provider.dart
│   ├── talk_provider.dart
│   └── parent_provider.dart
├── screens/
│   ├── my_toys/my_toys_screen.dart
│   ├── create_toy/create_toy_screen.dart
│   ├── talk/talk_screen.dart
│   └── parent/parent_screen.dart
└── widgets/
    ├── toy_card.dart
    ├── chat_bubble.dart
    ├── record_button.dart
    ├── magic_animation.dart
    └── date_slider.dart
```

---

*End of flutter-init SKILL.md*
