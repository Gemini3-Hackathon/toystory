# Frontend Specification (Flutter)

> 프론트엔드 에이전트가 참조하는 명세서.
> API 계약은 반드시 [api-contract.md](./api-contract.md)를 따른다.

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | Dart |
| 프레임워크 | Flutter |
| 상태 관리 | (예: Riverpod / Bloc / Provider) |
| HTTP 클라이언트 | (예: Dio / http) |
| 라우팅 | (예: GoRouter / auto_route) |
| 로컬 저장소 | (예: SharedPreferences / Hive) |

## 프로젝트 구조

```
frontend/
├── lib/
│   ├── main.dart                # 엔트리포인트
│   ├── app.dart                 # MaterialApp 설정
│   ├── config/
│   │   └── api_config.dart      # API Base URL 등
│   ├── models/                  # 데이터 모델 (fromJson/toJson)
│   │   └── user.dart
│   ├── services/                # API 호출 레이어
│   │   └── auth_service.dart
│   ├── providers/               # 상태 관리
│   │   └── auth_provider.dart
│   ├── screens/                 # 페이지 (화면 단위)
│   │   ├── home_screen.dart
│   │   └── login_screen.dart
│   ├── widgets/                 # 재사용 위젯
│   │   └── common/
│   └── utils/                   # 유틸리티
├── assets/
├── pubspec.yaml
└── analysis_options.yaml
```

> 위는 예시입니다. 실제 구조에 맞게 수정하세요.

## 화면 구성

| 라우트 | 화면 | 인증 필요 | 설명 |
|--------|------|-----------|------|
| `/` | HomeScreen | No | 랜딩 |
| `/login` | LoginScreen | No | - |
| `/signup` | SignupScreen | No | - |
| `/dashboard` | DashboardScreen | Yes | - |
| | | | |

## API 연동 규칙

### Base 설정
```dart
// 예시: config/api_config.dart
class ApiConfig {
  static const String baseUrl = 'http://localhost:8000/api/v1';
  // Android 에뮬레이터: 'http://10.0.2.2:8000/api/v1'
}
```

### 모델 클래스
- api-contract.md의 데이터 모델을 `models/` 디렉토리에 Dart 클래스로 정의
- `fromJson()` / `toJson()` 필수 구현
- 응답은 항상 `{ success, data }` 또는 `{ success, error }` 형태

### 인증 토큰 처리
- 토큰 저장 위치: (예: SharedPreferences / FlutterSecureStorage)
- 요청 시 `Authorization: Bearer <token>` 헤더 자동 첨부 (Interceptor)
- 401 응답 시 로그인 화면으로 리다이렉트

## 주요 위젯

| 위젯 | 위치 | 역할 |
|------|------|------|
| `AppButton` | `widgets/common/app_button.dart` | 공통 버튼 |
| `AppTextField` | `widgets/common/app_text_field.dart` | 공통 텍스트 필드 |
| `AuthGuard` | `widgets/auth_guard.dart` | 인증 라우트 보호 |
| | | |

## 환경 변수 / 설정

| 항목 | 설명 | 예시 |
|------|------|------|
| API_BASE_URL | API 서버 주소 | `http://localhost:8000/api/v1` |

## 디자인 / UI 가이드

- 타겟 플랫폼: (예: iOS + Android / Web 포함)
- 디자인 시스템: (예: Material 3)
- 컬러 팔레트: (미정)
- 폰트: (미정)

## 구현 시 주의사항

- api-contract.md에 정의된 요청/응답 형식을 **정확히** 따를 것
- 에러 처리: 계약서의 에러 코드별로 적절한 UI 피드백 (SnackBar 등)
- 로딩 상태, 에러 상태 UI 반드시 구현
- 플랫폼별 차이 (Android 에뮬레이터 localhost 주소 등) 주의

---

## 변경 이력

| 날짜 | 변경 내용 | 작성자 |
|------|-----------|--------|
| 2026-02-28 | 초기 템플릿 생성 | - |
