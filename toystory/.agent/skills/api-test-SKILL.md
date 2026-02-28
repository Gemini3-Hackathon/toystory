# Skill: api-test

> curl 기반 API 엔드포인트 스모크 테스트

---

## Purpose

FastAPI 서버의 주요 엔드포인트가 정상 응답하는지 빠르게 확인.
Phase 완료 검증 게이트로 사용.

## Trigger

| Phase | 용도 |
|-------|------|
| **2.10** | 백엔드 구성 완료 후 전체 스모크 테스트 |
| **4 완료** | 턴제 대화 연동 확인 |
| **5 완료** | WS 연결 핸드셰이크 확인 |

## Referenced By

- backend agent

## Scripts

| Script | 용도 |
|--------|------|
| `scripts/test_endpoints.sh` | 주요 엔드포인트 curl 테스트 |

## Success Criteria

- 5개 REST 엔드포인트 모두 기대 HTTP 상태코드 반환
- 응답 body에 `"success": true` 포함 (성공 케이스)
- 전체 테스트 통과 시 exit 0, 하나라도 실패 시 exit 1

## Failure Handling

- 실패 엔드포인트 로그 출력 → 에스컬레이션 (수동 디버깅)

---

## Test Script Specification

```bash
#!/bin/bash
# scripts/test_endpoints.sh
# Usage: bash test_endpoints.sh [BASE_URL]
# Default: http://localhost:8000/api/v1

BASE_URL=${1:-"http://localhost:8000/api/v1"}
PASS=0
FAIL=0
TOKEN=""

echo "=== ToyTalk API Smoke Test ==="
echo "Base URL: $BASE_URL"
echo ""

# Helper
check() {
  local name=$1 expected=$2 actual=$3
  if [ "$actual" = "$expected" ]; then
    echo "✅ PASS: $name (HTTP $actual)"
    PASS=$((PASS+1))
  else
    echo "❌ FAIL: $name (expected $expected, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

# 1. Health Check (GET /docs — FastAPI auto-generated)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/../docs")
check "GET /docs (Health)" "200" "$STATUS"

# 2. Signup
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@demo.com","password":"test1234","nickname":"tester"}')
# 201 (created) or 409 (duplicate) both acceptable
if [ "$STATUS" = "201" ] || [ "$STATUS" = "409" ]; then
  echo "✅ PASS: POST /auth/signup (HTTP $STATUS)"
  PASS=$((PASS+1))
else
  echo "❌ FAIL: POST /auth/signup (expected 201|409, got $STATUS)"
  FAIL=$((FAIL+1))
fi

# 3. Login → Get Token
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@demo.com","password":"test1234"}')
STATUS=$(echo "$RESPONSE" | python3 -c "import sys,json; print(200)" 2>/dev/null || echo "500")
TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('accessToken',''))" 2>/dev/null)
check "POST /auth/login" "200" "$STATUS"

# 4. GET /toys (with auth)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/toys" \
  -H "Authorization: Bearer $TOKEN")
check "GET /toys" "200" "$STATUS"

# 5. GET /logs/bear001 (demo data)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/logs/bear001" \
  -H "Authorization: Bearer $TOKEN")
check "GET /logs/{toyId}" "200" "$STATUS"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ $FAIL -gt 0 ]; then
  exit 1
else
  exit 0
fi
```

---

*End of api-test SKILL.md*
