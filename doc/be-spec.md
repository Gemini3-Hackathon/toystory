# Backend Specification

> 백엔드 에이전트가 참조하는 명세서.
> API 계약은 반드시 [api-contract.md](./api-contract.md)를 따른다.

## 기술 스택

| 항목 | 선택 |
|------|------|
| 언어 | (예: Python 3.12) |
| 프레임워크 | (예: FastAPI) |
| DB | (예: PostgreSQL 16) |
| ORM | (예: SQLAlchemy 2.x) |
| 인증 | (예: JWT) |
| 마이그레이션 | (예: Alembic) |
| 테스트 | (예: pytest) |
| 배포 | (예: Docker) |

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py              # 엔트리포인트
│   ├── config.py            # 설정 (환경변수 로딩)
│   ├── database.py          # DB 연결, 세션 관리
│   ├── dependencies.py      # 공통 의존성 (get_current_user 등)
│   ├── models/              # DB 모델 (ORM)
│   │   └── user.py
│   ├── schemas/             # 요청/응답 스키마
│   │   └── user.py
│   ├── routers/             # API 라우터
│   │   └── auth.py
│   ├── services/            # 비즈니스 로직
│   │   └── auth_service.py
│   └── utils/               # 유틸리티
│       └── security.py      # 해싱, JWT 생성/검증
├── tests/
│   └── test_auth.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

> 위는 예시입니다. 실제 구조에 맞게 수정하세요.

## DB 스키마

### users
| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | - |
| email | VARCHAR(255) | UNIQUE, NOT NULL | - |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt |
| nickname | VARCHAR(20) | NOT NULL | 2~20자 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | - |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | - |

### (테이블명)
| 컬럼 | 타입 | 제약조건 | 설명 |
|------|------|----------|------|
| id | UUID | PK | - |

## API 연동 규칙

### 라우터 등록
- api-contract.md의 Base URL(`/api/v1`)을 prefix로 사용
- 도메인별 라우터 분리 (auth, user, ...)

```python
# 예시: main.py
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
```

### 요청/응답 스키마
- api-contract.md의 데이터 모델을 `schemas/`에 Pydantic 모델로 정의
- 응답은 항상 공통 래퍼 형식을 따름

```python
# 예시: schemas/common.py
class SuccessResponse(BaseModel):
    success: bool = True
    data: Any

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
```

### 인증 미들웨어
- JWT 토큰 검증 → `dependencies.py`의 `get_current_user` 사용
- 인증 필요 엔드포인트에 `Depends(get_current_user)` 적용
- 토큰 만료 시 401 응답

## 에러 처리 규칙

- api-contract.md의 공통 에러 형식을 **반드시** 따를 것
- 도메인별 에러 코드는 api-contract.md에 정의된 것만 사용
- 예외 핸들러로 일관된 에러 응답 보장

```python
# 예시
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.detail.get("code", "UNKNOWN"),
                "message": exc.detail.get("message", "")
            }
        }
    )
```

## 환경 변수

| 변수명 | 설명 | 예시 |
|--------|------|------|
| DATABASE_URL | DB 접속 URL | `postgresql://user:pass@localhost:5432/toystory` |
| JWT_SECRET | JWT 서명 키 | `your-secret-key` |
| JWT_EXPIRE_MINUTES | 액세스 토큰 만료(분) | `60` |
| REFRESH_TOKEN_EXPIRE_DAYS | 리프레시 토큰 만료(일) | `7` |
| CORS_ORIGINS | 허용 오리진 (콤마 구분) | `http://localhost:3000` |

## CORS 설정

- 프론트엔드 개발 서버 허용
- Flutter Web: `http://localhost:3000` 등 (포트 확인 필요)
- 모바일 앱은 CORS 불필요 (네이티브 HTTP)

## 외부 연동 (해당 시)

| 서비스 | 용도 | 비고 |
|--------|------|------|
| (예: AWS S3) | (예: 이미지 저장) | - |
| (예: Redis) | (예: 캐싱/세션) | - |

## 구현 시 주의사항

- api-contract.md에 정의된 요청/응답 형식을 **정확히** 따를 것
- 비밀번호는 반드시 해싱하여 저장 (bcrypt 등)
- DB 마이그레이션 도구 사용 (스키마 변경 추적)
- 민감 정보(시크릿, DB 비밀번호)는 `.env`로 관리, 커밋 금지
- API 응답 시 password_hash 등 민감 필드 노출 금지

---

## 변경 이력

| 날짜 | 변경 내용 | 작성자 |
|------|-----------|--------|
| 2026-02-28 | 초기 템플릿 생성 | - |
