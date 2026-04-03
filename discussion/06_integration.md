# 6. 기존 프로젝트 연계 (economic-dashboard)

## 토론 참여자
- PM (기획자) / FE (프론트엔드 개발자) / ECO (경제 도메인 전문가) / DA (데이터 아키텍트)

---

### PM: 두 프로젝트의 관계를 정리하면

| | economic-dashboard | economic-map |
|---|---|---|
| 역할 | 경제 브리핑 대시보드 | 경제 지표 관계도 |
| 핵심 기능 | 실시간 데이터 표시 | 지표 간 관계 시각화 |
| 데이터 | FRED API (실시간) | 정적 관계 데이터 |
| 사용 시점 | 매일 브리핑 확인 | 관계 학습/시뮬레이션 |
| URL | machomehe.github.io/economic-dashboard | machomehe.github.io/economic-map |

**시너지 포인트:**
- dashboard에서 "금리가 5.25%"를 보고 → "그래서 뭐가 어떻게 되지?" → map으로 이동
- map에서 지표 탭하면 → "현재 값: 5.25% (출처: dashboard)" 표시

### DA: 연동 방식은 세 가지가 있습니다

**방식 1: 링크 연동 (가장 단순)**
- dashboard에 "관계도 보기" 링크 추가
- map에 "대시보드 보기" 링크 추가
- 각 지표 팝업에 dashboard의 해당 지표 직링크

**방식 2: 데이터 공유**
- dashboard가 FRED에서 가져온 최신 값을 JSON으로 저장
- map이 이 JSON을 fetch해서 노드에 현재값 표시
- 공유 JSON 파일: 별도 리포 또는 한쪽에서 호스팅

**방식 3: 통합 앱**
- 하나의 앱으로 합치기
- 탭 구조: [브리핑] [관계도] [시나리오]

### FE: 방식 3은 추천하지 않습니다

**반론:** 각 프로젝트가 충분히 복잡하고, 합치면 유지보수가 어려워집니다. 특히 코딩 초보 사용자 입장에서 하나의 거대한 프로젝트보다 **두 개의 작은 프로젝트**가 관리하기 쉽습니다.

**추천: 방식 1 + 2 결합**
- Phase 1: 링크 연동 (상호 이동)
- Phase 2: 데이터 공유 (dashboard의 최신 데이터를 map에서 표시)

### ECO: 데이터 공유에서 가장 유용한 건 "추세" 정보입니다

단순히 "현재 CPI = 3.2%"보다는:
- "CPI 3.2%, 전월 대비 ↑0.1%p, 3개월 연속 상승"
- 이 추세 정보가 관계도의 **시뮬레이션에 현실감**을 더해줌

예: 사용자가 "인플레이션" 노드를 탭하면
- 팝업: "인플레이션 (CPI 3.2%, 상승 추세 ↗)"
- 시뮬레이션: "현재 상승 추세이므로 → 금리 인상 압력 → 성장주 하락 압력"

**이 컨텍스트가 있으면 교과서적 관계도가 아니라 "지금 시장에서 실제로 작동하는 관계도"가 됩니다.**

### DA: 기술적으로 구현하면

dashboard가 FRED 데이터를 이미 가져오고 있으므로:

1. dashboard에서 `data/latest-values.json` 생성 (GitHub Actions 활용)
```json
{
  "lastUpdated": "2026-04-03T09:00:00Z",
  "values": {
    "FEDFUNDS": {"value": 4.50, "change": 0, "trend": "flat"},
    "CPIAUCSL": {"value": 3.2, "changeYoY": 0.1, "trend": "up"},
    "DGS10": {"value": 4.15, "change": -0.05, "trend": "down"}
  }
}
```

2. map에서 이 파일을 fetch (CORS: 같은 github.io 도메인이라 문제 없음)
```js
fetch('https://machomehe.github.io/economic-dashboard/data/latest-values.json')
```

3. 노드에 현재값 + 추세 표시

### PM: 사용자 동선을 다시 정리하면

**일일 루틴:**
1. 아침: economic-dashboard에서 오늘 브리핑 확인 (숫자 위주)
2. 궁금한 게 있으면: economic-map으로 이동해서 관계/시뮬레이션 확인
3. 톡방에서 새로운 인사이트 획득 → map에 추가 (Phase 2)

**이벤트 발생 시:**
1. FOMC 결과 발표 → dashboard에서 확인
2. "금리 동결이 뭘 의미하지?" → map에서 시뮬레이션
3. "아, 성장주에 호재구나" → 투자 판단

### FE: 상호 링크를 구현하는 구체적 방법

**dashboard → map:**
- 각 지표 카드에 🔗 아이콘 → 클릭하면 `economic-map/?focus=rate` 형태로 이동
- map에서 URL 파라미터로 특정 노드를 자동 선택/포커스

**map → dashboard:**
- 노드 팝업에 "실시간 데이터 보기" 링크 → `economic-dashboard/#rate` 형태로 이동

이 URL 기반 딥링크가 가장 단순하면서 효과적입니다.

---

## 합의된 연동 계획

### Phase 1: 상호 링크
- dashboard에 "관계도 보기" 버튼/링크
- map에 "대시보드 보기" 버튼/링크
- URL 파라미터로 특정 지표 직접 연결 (?focus=nodeId)

### Phase 2: 데이터 공유
- dashboard가 latest-values.json 생성 (GitHub Actions)
- map이 fetch해서 노드에 현재값 + 추세 표시
- FRED 코드 매핑: nodes.json의 dataSource.fred 필드 활용

### 핵심 원칙
- 별도 프로젝트 유지 (합치지 않음)
- URL 기반 딥링크로 연결
- 데이터 공유는 JSON 파일 기반 (API 서버 없음)
