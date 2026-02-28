# Skill: db-setup

> SQLite 데이터베이스 초기화 + 데모 시드 데이터 삽입

---

## Purpose

- 5개 테이블 DDL 실행 (toys, sessions, messages, daily_logs, weekly_summaries)
- 해커톤 데모용 시드 데이터 삽입 (toys 2건 + daily_logs 3건 + weekly_summaries 1건)

## Trigger

| Phase | 작업 |
|-------|------|
| **0.5** | DDL 실행 → 5개 테이블 생성 |
| **9.1** | 데모 시드 데이터 INSERT |

## Referenced By

- backend agent (Phase 0.5, 9.1)

## Scripts

| Script | 용도 | 실행 명령 |
|--------|------|-----------|
| `scripts/init_tables.py` | DDL 실행 — 5개 테이블 생성 | `python scripts/init_tables.py` |
| `scripts/seed_demo.py` | 데모 데이터 INSERT | `python scripts/seed_demo.py` |

## Success Criteria

| 검증 | 명령 | 기대 결과 |
|------|------|-----------|
| 테이블 존재 | `sqlite3 toytalk.db ".tables"` | toys sessions messages daily_logs weekly_summaries |
| 시드 데이터 | `sqlite3 toytalk.db "SELECT count(*) FROM toys"` | 2 |

## Failure Handling

- DDL 실패 → 자동 재시도 1회 → 실패 시 에스컬레이션
- 시드 INSERT 실패 → 로그 기록 + 수동 삽입 안내

---

## DDL Reference

5개 테이블의 전체 DDL은 `.agent/agents/backend/AGENT.md` §7에 정의됨.

## Demo Seed Data Specification

### toys (2건)

```sql
-- 곰돌이 캐릭터
INSERT INTO toys (toy_id, owner_uid, toy_name, type, primary_color, secondary_color,
  features, expression, texture, voice_profile, child_name, avatar_path, original_photo_path)
VALUES (
  'bear001', 'parent-demo-uid', '곰돌이', 'bear', '#8B4513', '#F5DEB3',
  '["round_ears", "button_eyes", "bow_tie_red"]', 'smiling', 'plush_fuzzy',
  '{"style":"ppororo","pitchShift":3,"speedRate":1.0,"ttsPrompt":"따뜻하고 포근한, 밝은 목소리","autoMatched":true}',
  '혜진', '/uploads/avatars/bear001.png', '/uploads/photos/bear001_original.jpg'
);

-- 공룡 캐릭터
INSERT INTO toys (toy_id, owner_uid, toy_name, type, primary_color, secondary_color,
  features, expression, texture, voice_profile, child_name, avatar_path, original_photo_path)
VALUES (
  'dino001', 'parent-demo-uid', '다이노', 'dinosaur', '#228B22', '#90EE90',
  '["spikes", "big_eyes", "short_arms"]', 'excited', 'plastic_smooth',
  '{"style":"tayo","pitchShift":1,"speedRate":1.1,"ttsPrompt":"또박또박하고 에너지 넘치는","autoMatched":true}',
  '혜진', '/uploads/avatars/dino001.png', '/uploads/photos/dino001_original.jpg'
);
```

### daily_logs (3일분)

```sql
INSERT INTO daily_logs (date, toy_id, total_messages, conversations, is_summarized) VALUES
('2026-02-26', 'bear001', 8,
 '[{"time":"14:30:15","role":"user","text":"곰돌이, 오늘 유치원에서 그림 그렸어!"},
   {"time":"14:30:18","role":"assistant","text":"우와! 뭐 그렸어? 곰돌이도 보고 싶다!"},
   {"time":"14:30:25","role":"user","text":"무지개!"},
   {"time":"14:30:28","role":"assistant","text":"와~ 무지개! 어떤 색으로 그렸어?"},
   {"time":"14:31:00","role":"user","text":"빨간색이랑 파란색이랑 노란색!"},
   {"time":"14:31:03","role":"assistant","text":"와~ 진짜 예쁜 무지개다! 곰돌이도 그려줘~"},
   {"time":"14:31:15","role":"user","text":"응 다음에 그려줄게!"},
   {"time":"14:31:18","role":"assistant","text":"약속이다! 기다릴게~"}]',
 1),

('2026-02-27', 'bear001', 6,
 '[{"time":"10:00:05","role":"user","text":"곰돌이 안녕!"},
   {"time":"10:00:08","role":"assistant","text":"안녕 혜진아! 오늘 기분 어때?"},
   {"time":"10:00:15","role":"user","text":"좀 슬퍼... 친구랑 싸웠어"},
   {"time":"10:00:18","role":"assistant","text":"혜진아, 그러구나. 내가 안아줄게!"},
   {"time":"10:00:30","role":"user","text":"고마워 곰돌이"},
   {"time":"10:00:33","role":"assistant","text":"곰돌이가 항상 옆에 있을게! 힘내~"}]',
 1),

('2026-02-28', 'bear001', 4,
 '[{"time":"15:00:10","role":"user","text":"곰돌이, 어제 무지개 그렸다고 했잖아"},
   {"time":"15:00:13","role":"assistant","text":"응! 무지개 그림 많이 그렸어? 어떤 색이었어?"},
   {"time":"15:00:20","role":"user","text":"빨간색! 근데 오늘은 공룡 그렸어"},
   {"time":"15:00:23","role":"assistant","text":"오~ 공룡! 어떤 공룡 그렸어? 티라노?"}]',
 0);
```

### weekly_summaries (1건)

```sql
INSERT INTO weekly_summaries (week_id, toy_id, date_range, total_sessions, total_messages,
  summary, topics, emotions, memorable_events) VALUES
('2026-W09', 'bear001',
 '{"start":"2026-02-24","end":"2026-03-02"}',
 5, 47,
 '이번 주에 아이는 유치원에서 무지개 그림을 그렸다고 자랑했고, 곰돌이와 함께 숫자 세기 놀이를 했습니다. 수요일에는 조금 슬퍼하다고 했는데, 친구와 싸웠다고 합니다. 곰돌이가 위로해주자 금방 기분이 나아졌습니다.',
 '["유치원", "무지개 그림", "숫자 세기", "친구 이야기"]',
 '["즐거움", "자랑스러움", "슬픔", "위로받음"]',
 '["무지개 그림 자랑", "친구와 싸움 → 위로 → 회복"]');
```

---

*End of db-setup SKILL.md*
