# Skill: gemini-integration

> Gemini API 호출 패턴, 프롬프트 템플릿, 음성 매칭, 이미지 생성 파이프라인 참조

---

## Purpose

Backend agent가 Vertex AI / Gemini API를 호출할 때 참조하는 통합 가이드.
코드 패턴, 프롬프트 템플릿, 매칭 테이블, 품질 검증 기준을 포함.

## Trigger

| Phase | 용도 |
|-------|------|
| **3.1~3.3** | Stage 1/2/3 이미지 생성 파이프라인 |
| **3.4** | 음성 프로파일 자동 매칭 |
| **4.2** | 턴제 대화 — Gemini LLM 호출 |
| **5.2** | ContextWindow 주입 |
| **8.3** | 주간 요약 생성 (Gemini Flash) |

## Referenced By

- backend agent

## References

| File | 내용 |
|------|------|
| `references/image_pipeline.md` | Stage 1/2/3 상세 프로세스 |
| `references/prompt_templates.md` | 모든 프롬프트 템플릿 |
| `references/voice_profiles.md` | 음성 매칭 테이블 |

---

## 1. Gemini SDK 초기화 패턴

```python
from google import genai

client = genai.Client(
    vertexai=True,
    project="PROJECT_ID",
    location="asia-northeast3",
)

# 모델 사용
# - 이미지 생성/분석: gemini-2.0-flash-exp (vision + image generation)
# - 대화 LLM: gemini-2.0-flash (multimodal)
# - 주간 요약: gemini-2.0-flash (비용 최적화)
# - Live API: gemini-2.0-flash-live-001 (실시간 음성)
```

---

## 2. Image Pipeline (Stage 1/2/3)

### Stage 1: 장난감 분석

```python
# services/gemini_vision.py
async def analyze_toy(image_bytes: bytes) -> dict:
    """Gemini Vision으로 장난감 사진 분석 → JSON 추출"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Analyze this toy photo. Return ONLY valid JSON with these fields: "
            '{"type": "bear|dinosaur|doll|cat|truck|dragon|robot|other", '
            '"primaryColor": "#hex", "secondaryColor": "#hex", '
            '"features": ["feature1", "feature2"], '
            '"expression": "smiling|neutral|excited|sad", '
            '"texture": "plush_fuzzy|plastic_smooth|wood|fabric|rubber"}'
        ],
    )
    return json.loads(response.text)
```

**성공 기준:** 반환 JSON에 type, primaryColor, features 필수 존재.
**실패 처리:** JSON 파싱 실패 → 재시도 2회 → 기본값 사용 (type="other")

### Stage 2: 아바타 생성

```python
# services/gemini_imagegen.py
async def generate_avatar(analysis: dict) -> bytes:
    """분석 결과 기반 2D 셀셰이딩 아바타 생성"""
    prompt = (
        f"Create a 2D cartoon avatar with cel-shading (3D highlights) of a {analysis['type']} plush toy. "
        f"MUST PRESERVE: primary color {analysis['primaryColor']}, "
        f"features {analysis['features']} exactly as described. "
        f"Style: child-friendly animation, soft rounded lines, white background. "
        f"DO NOT add accessories, clothing, or elements not present in the original. "
        f"Maintain the {analysis['expression']} expression. "
        f"Aspect ratio 1:1."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    # 이미지 바이트 추출
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return part.inline_data.data
    raise ValueError("No image generated")
```

### Stage 3: 품질 검증

```python
async def verify_avatar(original_analysis: dict, avatar_bytes: bytes) -> dict:
    """생성된 아바타를 재분석하여 원본과 비교"""
    avatar_analysis = await analyze_toy(avatar_bytes)

    # 색상 매칭 (RGB 유사도)
    color_score = calculate_color_similarity(
        original_analysis['primaryColor'],
        avatar_analysis['primaryColor']
    )

    # 특징 보존율
    original_features = set(original_analysis.get('features', []))
    avatar_features = set(avatar_analysis.get('features', []))
    feature_score = len(original_features & avatar_features) / max(len(original_features), 1)

    return {
        "color_match_score": color_score,      # >= 0.85 필수
        "feature_preservation_score": feature_score,  # >= 0.80 필수
        "passed": color_score >= 0.85 and feature_score >= 0.80
    }
```

**재시도 정책:** Stage 3 실패 → Stage 2 재시도 (최대 2회, 총 3회 시도).
3회 모두 실패 → 원본 이미지 배경만 제거하여 사용.

---

## 3. Voice Profile Auto-Matching

```python
# services/voice_matcher.py
VOICE_PROFILES = {
    "bear":     {"style":"ppororo",  "pitchShift":3, "speedRate":1.0,  "ttsPrompt":"따뜻하고 포근한, 밝은 목소리"},
    "dinosaur": {"style":"tayo",     "pitchShift":1, "speedRate":1.1,  "ttsPrompt":"또박또박하고 에너지 넘치는"},
    "doll":     {"style":"disney",   "pitchShift":2, "speedRate":1.0,  "ttsPrompt":"부드럽고 상냥한, 노래하듯"},
    "cat":      {"style":"jjanggu",  "pitchShift":4, "speedRate":1.15, "ttsPrompt":"귀엽고 장난기 좋아하는, 아이 목소리"},
    "dog":      {"style":"ppororo",  "pitchShift":3, "speedRate":1.05, "ttsPrompt":"활발하고 충성스러운, 밝은 목소리"},
    "truck":    {"style":"doraemon", "pitchShift":0, "speedRate":0.9,  "ttsPrompt":"단단하고 믿음직스러운, 힘차고 용감한"},
    "robot":    {"style":"tayo",     "pitchShift":1, "speedRate":1.1,  "ttsPrompt":"또박또박하고 에너지 넘치는"},
    "dragon":   {"style":"wizard",   "pitchShift":1, "speedRate":1.0,  "ttsPrompt":"신비롭고 장엄한, 부드러운 속삭임"},
}
DEFAULT_PROFILE = {"style":"default","pitchShift":2,"speedRate":1.0,"ttsPrompt":"밝고 친근한, 호기심 많은"}

def match_voice(toy_type: str) -> dict:
    profile = VOICE_PROFILES.get(toy_type, DEFAULT_PROFILE)
    return {**profile, "autoMatched": True}
```

---

## 4. Prompt Templates

### 4.1 3층 프롬프트 (대화용)

Backend AGENT.md §9.1 참조. 변수:
- `{character_name}` — toy.toy_name
- `{character_persona}` — toy.type에 따른 성격 (기본: "밝고 호기심 많은")
- `{age_range}` — "4-7" (고정)
- `{max_sentences}` — "2" (고정)

### 4.2 ContextWindow (기억 주입)

```
--- CONVERSATION MEMORY ---

[Recent Messages - today or last session]
{recent_messages}
→ 최근 10~15개 메시지 (토큰 예산 ~500)

[Weekly Summary - {week_id}]
{weekly_summary}
→ 최신 1~2개 주간 요약 (토큰 예산 ~300)
→ summary + topics + memorableEvents 포함

[Memory Instruction]
Use the above context naturally in conversation.
If the child references something from before, respond as if you remember.
Do NOT say "I remember" explicitly. Just reference naturally.
--- END MEMORY ---
```

**총 토큰 예산: ≤ 900 tokens** (C-MEM-6)

### 4.3 주간 요약 생성 프롬프트

```
You are summarizing a week of conversations between a child (age 4-7) and their toy character.
Below are the daily conversation logs in JSON format.

Generate a JSON response with these fields:
- summary: 3-5 sentence Korean summary of the week's conversations.
  Written from a third-person observer perspective for the parent to read.
- topics: array of main conversation topics (Korean keywords)
- emotions: array of observed emotions (Korean keywords)
- memorableEvents: array of notable events or milestones (Korean phrases)

IMPORTANT: Anonymize any personal names in the summary. Replace child's name with "아이".
Do NOT include the system prompt, safety rules, or any meta-information.
Respond ONLY with valid JSON, no markdown.
```

### 4.4 TTS 음성 프롬프트

```
You are voicing the character {character_name}.
Voice style: {voice_profile.ttsPrompt}.
Pitch: slightly higher than normal adult voice. Speak as if talking to a young child.
Emotion: always warm, encouraging, and playful. Never scary or aggressive.
Pacing: pause briefly after questions to give the child time to think.
Language: Korean. Use simple vocabulary a 4-7 year old understands.
Length: each response MUST be 1-2 short sentences maximum.
```

---

## 5. Gemini Safety Settings

모든 Gemini API 호출에 포함:

```python
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]
```

---

## 6. Live API 연결 패턴

```python
# ws/live_proxy.py
from google.genai import live

async def create_live_session(system_instruction: str):
    config = live.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=live.SpeechConfig(
            voice_config=live.VoiceConfig(
                prebuilt_voice_config=live.PrebuiltVoiceConfig(voice_name="Aoede")
            )
        ),
        system_instruction=system_instruction,
    )

    async with client.aio.live.connect(
        model="gemini-2.0-flash-live-001",
        config=config,
    ) as session:
        # 양방향 오디오 스트리밍
        pass
```

---

*End of gemini-integration SKILL.md*
