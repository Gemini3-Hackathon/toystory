# API Contract

> 프론트엔드/백엔드 에이전트가 공통으로 참조하는 API 계약서.
> 이 문서가 Single Source of Truth. 양쪽 모두 이 문서를 기준으로 개발한다.

## Base URL

| 환경 | URL |
|------|-----|
| 로컬 개발 | `http://localhost:8000/api/v1` |
| 스테이징 | `(미정)` |
| 프로덕션 | `(미정)` |

## 공통 규칙

### 요청 형식
- Content-Type: `application/json`
- 인증: `Authorization: Bearer <token>` (인증 필요 API에 한함)

### 응답 형식
```json
// 성공
{
  "success": true,
  "data": { ... }
}

// 에러
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사람이 읽을 수 있는 메시지"
  }
}
```

### 공통 HTTP 상태 코드
| 코드 | 의미 |
|------|------|
| 200 | 성공 |
| 201 | 생성 성공 |
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 내부 오류 |

---

## API 엔드포인트

<!--
  아래 예시를 복사해서 실제 API를 추가하세요.
  각 API는 프론트/백 모두가 동의한 계약입니다.
-->

### 1. 인증 (Auth)

#### `POST /auth/signup`
회원가입

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string (min 8자)",
  "nickname": "string (2~20자)"
}
```

**Response 201:**
```json
{
  "success": true,
  "data": {
    "userId": "uuid",
    "email": "user@example.com",
    "nickname": "string",
    "createdAt": "2026-02-28T00:00:00Z"
  }
}
```

**Error Cases:**
| 코드 | code | 조건 |
|------|------|------|
| 409 | `DUPLICATE_EMAIL` | 이미 가입된 이메일 |
| 400 | `INVALID_INPUT` | 유효성 검증 실패 |

---

#### `POST /auth/login`
로그인

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response 200:**
```json
{
  "success": true,
  "data": {
    "accessToken": "jwt-string",
    "refreshToken": "jwt-string",
    "user": {
      "userId": "uuid",
      "email": "user@example.com",
      "nickname": "string"
    }
  }
}
```

---

<!-- 아래부터 실제 API를 추가하세요 -->

### 2. (도메인 이름)

#### `METHOD /path`
설명

**인증 필요:** Yes / No

**Request Body / Query Params:**
```json
{
}
```

**Response CODE:**
```json
{
  "success": true,
  "data": {
  }
}
```

**Error Cases:**
| 코드 | code | 조건 |
|------|------|------|

---

## 데이터 모델 (공유 타입)

> FE/BE 양쪽에서 동일하게 사용하는 데이터 구조를 여기에 정의한다.

### User
```
{
  userId: string (uuid)
  email: string
  nickname: string (2~20자)
  createdAt: string (ISO 8601)
  updatedAt: string (ISO 8601)
}
```

### (모델명)
```
{
  id: string (uuid)
  // 필드 추가
}
```

---

## WebSocket / 실시간 통신 (해당 시)

<!-- 실시간 기능이 필요하면 아래 템플릿을 사용하세요 -->

### 이벤트: `event_name`
**방향:** Client -> Server / Server -> Client

**Payload:**
```json
{
}
```

---

## 변경 이력

| 날짜 | 변경 내용 | 작성자 |
|------|-----------|--------|
| 2026-02-28 | 초기 템플릿 생성 | - |
