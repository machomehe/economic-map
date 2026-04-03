# 5. 자동화 파이프라인

## 토론 참여자
- PM (기획자) / FE (프론트엔드 개발자) / ECO (경제 도메인 전문가) / DA (데이터 아키텍트)

---

### PM: 사용자의 꿈의 시나리오를 먼저 그려봅시다

사용자가 원하는 이상적 흐름:

```
경제 톡방에서 인사이트 캡처 (스크린샷/텍스트 복사)
    ↓
AI가 자동 분석
    ↓
"새로운 지표 관계가 발견되었습니다" 알림
    ↓
관계도에 자동 추가 (또는 승인 후 추가)
    ↓
시간이 지나면서 나만의 투자 매뉴얼 완성
```

이걸 현실적으로 어디까지 가능하고, 어떻게 단계적으로 구현할 수 있을까요?

### DA: 기술적으로 분해하면 이런 파이프라인입니다

```
Input          →  Processing       →  Output           →  Action
텍스트/이미지   →  AI 분석(LLM)     →  구조화된 데이터   →  data.json 업데이트
```

각 단계별 현실적 옵션:

**1. Input (입력):**
- a) 텍스트 직접 입력 (웹에서 텍스트 박스)
- b) 스크린샷 업로드 (OCR → 텍스트)
- c) 클립보드 붙여넣기
- d) 카카오톡 공유하기 → 앱으로 전달 (PWA 필요)
- e) Google Drive 폴더 모니터링 (이미 연동됨!)

**2. Processing (AI 분석):**
- a) Claude API 직접 호출
- b) GPT API 직접 호출
- c) Claude Code CLI (로컬)
- d) Google Apps Script (Drive 연동 시)
- e) GitHub Actions (자동화)

**3. Output (결과):**
- 새 노드 제안 (ID, 이름, 카테고리, 설명)
- 새 링크 제안 (source, target, 관계, 설명)
- 이벤트 기록 (날짜, 내용, 영향)

**4. Action (적용):**
- 자동 적용 → data.json 직접 수정
- 승인 후 적용 → 사용자가 확인 후 추가
- PR 생성 → GitHub에서 검토 후 머지

### ECO: AI 분석의 정확도가 관건입니다

톡방 메시지를 AI에 넣으면 결과가 매번 다를 수 있어요. 예를 들어:

입력: "달러가 강세면 원화 약세고 외국인이 빠지니까 코스피 하락 압력"

AI가 추출해야 하는 것:
```json
{
  "relationships": [
    {"source": "dollar", "target": "krw", "type": "반비례"},
    {"source": "krw", "target": "foreign", "type": "비례"},
    {"source": "foreign", "target": "kospi", "type": "비례"}
  ],
  "newNodes": [
    {"id": "kospi", "label": "코스피", "category": "주식"}
  ]
}
```

**문제점:**
1. "코스피"가 기존 데이터에 없으면? → 새 노드로 추가할지 판단
2. 이미 있는 관계와 충돌하면? → 중복 처리
3. 잘못된 관계를 AI가 추출하면? → 검증

**제안:** AI 분석 결과는 항상 **"제안"으로 표시**하고, 사용자가 승인하는 구조가 안전합니다.

### FE: 현실적으로 MVP에서 가능한 자동화 수준은?

**가장 단순한 버전 (Phase 2 목표):**

1. 웹앱에 "텍스트 입력" 폼 추가
2. 사용자가 톡방 내용을 붙여넣기
3. 프론트엔드에서 Claude API 호출 (사용자의 API 키 사용)
4. AI가 구조화된 JSON 반환
5. "이 관계를 추가하시겠습니까?" 확인 UI
6. 확인하면 localStorage에 저장 (또는 data.json 다운로드)

**문제:** API 키를 프론트엔드에 넣으면 보안 이슈. 하지만 개인 프로젝트이고 GitHub Pages에서 서버가 없으므로...

### DA: API 키 문제는 여러 우회법이 있습니다

1. **Cloudflare Workers / Vercel Serverless**: 간단한 프록시 서버. 무료 티어.
2. **사용자가 자기 API 키를 입력**: localStorage에 저장. 개인 프로젝트니 OK.
3. **GitHub Actions 기반**: 입력을 GitHub Issue로 생성 → Actions에서 AI 분석 → PR 생성 → 머지하면 data.json 업데이트

**추천: 옵션 3 (GitHub Actions 기반)**
- 이유: 서버 필요 없음, GitHub Pages와 자연스러운 연동, 이력 관리 자동
- 흐름: 사용자가 GitHub Issue에 톡방 내용 붙여넣기 → Actions가 Claude API로 분석 → PR 생성 → 사용자 확인 후 머지

### PM: 그건 코딩 초보한테 너무 어렵지 않나요?

GitHub Issue 작성, PR 머지... 이건 개발자 워크플로우예요. 사용자가 투자 초보 + 코딩 초보라는 걸 기억하세요.

**대안 제안:**
1. **가장 단순**: 웹앱에 입력 폼 → AI 분석 → 결과를 "이번 세션에만" 임시 추가 (localStorage)
2. **중간**: 입력 폼 → AI 분석 → 결과를 data.json 형식으로 다운로드 → 사용자가 GitHub에 업로드 (이것도 어렵긴 함)
3. **이상적**: 입력 폼 → 프록시 서버 → AI 분석 → GitHub API로 data.json 직접 업데이트 (OAuth 필요)

### DA: PM 의견에 동의합니다. 단계적으로 갑시다

**Phase 2A (최소 자동화):**
- 웹앱 내 텍스트 입력
- 사용자의 Claude API 키 (localStorage 저장)
- AI 분석 → 제안 UI → 승인하면 localStorage에 추가
- "내 커스텀 데이터 내보내기/가져오기" 버튼

**Phase 2B (반자동화):**
- Google Drive 연동 (이미 있는 MCP 활용)
- Drive의 "경제분석/1) 일간분석" 폴더에 새 파일 올리면
- GitHub Actions가 감지 → AI 분석 → data.json 업데이트 PR

**Phase 3 (자동화):**
- 카카오톡 공유 → PWA로 수신 → 자동 분석 → 관계도 업데이트
- (이건 PWA의 Web Share Target API 필요, 꽤 고급)

### ECO: AI 분석의 프롬프트 설계가 핵심입니다

어떤 방식이든 AI에게 보내는 프롬프트가 결과 품질을 결정합니다. 제안:

```
당신은 경제 지표 관계 분석기입니다.
아래 텍스트에서 경제 지표 간의 인과관계를 추출하세요.

기존 지표 목록: [data.json의 노드 ID 목록]

출력 형식:
{
  "newNodes": [...],     // 기존에 없는 새 지표
  "newLinks": [...],     // 새로운 관계
  "updatedLinks": [...], // 기존 관계의 수정/보강
  "event": {...},        // 이벤트 기록
  "confidence": 0.8      // 분석 신뢰도
}

규칙:
1. 기존 노드 ID와 매칭 가능하면 기존 ID 사용
2. 관계의 방향(인과)을 정확히 판단
3. 비례/반비례/조건부를 구분
4. 확신이 낮은 관계는 confidence를 낮게
5. 한국어 경제 용어를 정확히 이해
```

### FE: 프롬프트 자체를 data 폴더에 저장해서 관리하면 좋겠어요

`data/prompts/analyze.txt` 같은 형태로. 프롬프트 개선도 버전 관리가 되니까요.

---

## 합의된 자동화 로드맵

### Phase 2A — 최소 자동화 (웹앱 내)
- 텍스트 입력 폼
- 사용자 API 키 입력 (localStorage)
- Claude API → 구조화된 관계 추출
- 제안 UI → 승인 → localStorage 저장
- 커스텀 데이터 내보내기/가져오기

### Phase 2B — 반자동화 (GitHub Actions)
- Claude Code로 analysis prompt 실행
- data.json 자동 업데이트 PR 생성
- Google Drive 감지 연동 (가능하면)

### Phase 3 — 완전 자동화
- PWA + Web Share Target (카카오톡 공유 수신)
- 자동 분석 + 자동 추가 (승인 프로세스)
- 히스토리 + 롤백

### 핵심 원칙
1. **항상 사용자 승인 필요** — AI가 자동 추가하지 않음
2. **프롬프트도 버전 관리** — data/prompts/ 폴더
3. **단계적 복잡도 증가** — localStorage부터 시작
4. **기존 인프라 활용** — Google Drive MCP, GitHub Pages, GitHub Actions
