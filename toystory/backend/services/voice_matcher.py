"""
ToyTalk Backend — 음성 프로파일 자동 매칭
toy.type → voiceProfile JSON 생성
"""

VOICE_PROFILES: dict[str, dict] = {
    "bear": {
        "style": "ppororo",
        "pitchShift": 3,
        "speedRate": 1.0,
        "ttsPrompt": "따뜻하고 포근한, 밝은 목소리",
    },
    "dinosaur": {
        "style": "tayo",
        "pitchShift": 1,
        "speedRate": 1.1,
        "ttsPrompt": "또박또박하고 에너지 넘치는",
    },
    "doll": {
        "style": "disney",
        "pitchShift": 2,
        "speedRate": 1.0,
        "ttsPrompt": "부드럽고 상냥한, 노래하듯",
    },
    "cat": {
        "style": "jjanggu",
        "pitchShift": 4,
        "speedRate": 1.15,
        "ttsPrompt": "귀엽고 장난기 좋아하는, 아이 목소리",
    },
    "dog": {
        "style": "ppororo",
        "pitchShift": 3,
        "speedRate": 1.05,
        "ttsPrompt": "활발하고 충성스러운, 밝은 목소리",
    },
    "truck": {
        "style": "doraemon",
        "pitchShift": 0,
        "speedRate": 0.9,
        "ttsPrompt": "단단하고 믿음직스러운, 힘차고 용감한",
    },
    "robot": {
        "style": "tayo",
        "pitchShift": 1,
        "speedRate": 1.1,
        "ttsPrompt": "또박또박하고 에너지 넘치는",
    },
    "dragon": {
        "style": "wizard",
        "pitchShift": 1,
        "speedRate": 1.0,
        "ttsPrompt": "신비롭고 장엄한, 부드러운 속삭임",
    },
}

DEFAULT_PROFILE: dict = {
    "style": "default",
    "pitchShift": 2,
    "speedRate": 1.0,
    "ttsPrompt": "밝고 친근한, 호기심 많은",
}


def match_voice(toy_type: str) -> dict:
    """toy.type → voiceProfile 자동 매칭"""
    profile = VOICE_PROFILES.get(toy_type, DEFAULT_PROFILE)
    return {**profile, "autoMatched": True}
