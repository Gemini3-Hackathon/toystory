# Skill: build-verify

> Flutter 정적 분석 + Python 컴파일 + Docker 빌드 검증

---

## Purpose

매 Phase 완료 시 코드 품질 게이트로 사용.
빌드/컴파일 에러가 다음 Phase로 전파되지 않도록 차단.

## Trigger

- **매 Phase 완료 시** (Quality Gate)
- 특히 Phase 1.9, 2.9, 3.5, 5.5 완료 후 필수 실행

## Referenced By

- backend agent (Python 검증)
- frontend agent (Flutter 검증)

## Scripts

| Script | 용도 | 대상 |
|--------|------|------|
| `scripts/flutter_check.sh` | Flutter analyze + debug build | frontend/ |
| `scripts/python_check.sh` | Python compile check | backend/ |
| `scripts/docker_check.sh` | Docker build 검증 | backend/ |

## Success Criteria

| 검증 | 통과 기준 |
|------|-----------|
| flutter analyze | 0 errors (warnings 허용) |
| python compile | exit code 0 (모든 .py 파일) |
| docker build | exit code 0 (이미지 생성 성공) |

## Failure Handling

- 자동 재시도 2회 → 실패 시 에러 로그 출력 + 에스컬레이션
- 에러 메시지에서 파일명/라인 번호 추출하여 수정 힌트 제공

---

## Script Specifications

### flutter_check.sh

```bash
#!/bin/bash
# Flutter 정적 분석 + 디버그 빌드 확인
cd frontend || exit 1

echo "=== Flutter Analyze ==="
flutter analyze 2>&1
ANALYZE_EXIT=$?

if [ $ANALYZE_EXIT -ne 0 ]; then
  echo "❌ Flutter analyze failed"
  exit 1
fi

echo ""
echo "=== Flutter Build (debug APK) ==="
flutter build apk --debug 2>&1
BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
  echo "❌ Flutter build failed"
  exit 1
fi

echo "✅ Flutter checks passed"
exit 0
```

### python_check.sh

```bash
#!/bin/bash
# Python 모든 .py 파일 컴파일 검증
cd backend || exit 1

echo "=== Python Compile Check ==="
FAIL=0

for f in $(find . -name "*.py" -not -path "./.venv/*"); do
  python3 -m py_compile "$f" 2>&1
  if [ $? -ne 0 ]; then
    echo "❌ Compile failed: $f"
    FAIL=$((FAIL+1))
  fi
done

if [ $FAIL -gt 0 ]; then
  echo "❌ $FAIL file(s) failed compilation"
  exit 1
fi

echo "✅ All Python files compile successfully"
exit 0
```

### docker_check.sh

```bash
#!/bin/bash
# Docker build 검증 (빌드만 — 실행은 안 함)
cd backend || exit 1

echo "=== Docker Build Check ==="
docker build -t toytalk-api:test . 2>&1
BUILD_EXIT=$?

if [ $BUILD_EXIT -ne 0 ]; then
  echo "❌ Docker build failed"
  exit 1
fi

echo "✅ Docker build successful"
# 테스트 이미지 삭제
docker rmi toytalk-api:test 2>/dev/null
exit 0
```

---

*End of build-verify SKILL.md*
