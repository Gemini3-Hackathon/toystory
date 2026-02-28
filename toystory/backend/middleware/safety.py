"""
ToyTalk Backend — 2단계 안전 필터
Layer 1: Gemini Safety Settings (API 호출 시 적용)
Layer 2: Rule-based 키워드 + 패턴 매칭
"""

import re

# Layer 2: 차단 키워드 및 패턴
BLOCKED_KEYWORDS = [
    # 개인정보 요청
    "주소", "전화번호", "비밀번호", "주민등록", "집이 어디",
    # 위험한 행동
    "칼", "불", "약", "죽", "때려", "싸움",
    # 부적절한 콘텐츠
    "나쁜말", "욕",
]

BLOCKED_PATTERNS = [
    r"\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}",  # 전화번호
    r"\d{6}[-\s]?\d{7}",  # 주민번호
]

# 안전 대체 응답
SAFE_FALLBACK = "그건 잘 모르겠어! 대신 재미있는 이야기 해줄까?"


def check_safety(text: str) -> dict:
    """
    텍스트 안전성 검사
    Returns: {"safe": bool, "reason": str|None, "filtered_text": str}
    """
    if not text or not text.strip():
        return {"safe": True, "reason": None, "filtered_text": text}

    lower_text = text.lower().strip()

    # 키워드 검사
    for keyword in BLOCKED_KEYWORDS:
        if keyword in lower_text:
            return {
                "safe": False,
                "reason": f"blocked_keyword: {keyword}",
                "filtered_text": SAFE_FALLBACK,
            }

    # 패턴 검사
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text):
            return {
                "safe": False,
                "reason": f"blocked_pattern: {pattern}",
                "filtered_text": SAFE_FALLBACK,
            }

    return {"safe": True, "reason": None, "filtered_text": text}


def get_gemini_safety_settings() -> list[dict]:
    """Gemini API 호출 시 적용할 Safety Settings (Layer 1)"""
    return [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_LOW_AND_ABOVE",
        },
    ]
