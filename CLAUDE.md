# Economic Map 프로젝트

## 개요
경제 지표 간 인과관계를 시각화하는 인터랙티브 맵
- 배포: https://machomehe.github.io/economic-map/
- GitHub: https://github.com/machomehe/economic-map

## 기술 스택
- D3.js (CDN), Vanilla JS, 단일 index.html
- 데이터: data/data.json (노드+링크), data/values.json (FRED 실시간)
- Python: fetch_data.py (FRED 데이터), server.py (로컬 테스트)
- 배포: GitHub Pages (빌드 도구 없음)

## 현재 상태 (2026-04-07)
- Phase 1 MVP 대부분 완료 + 고객피드백 Phase 0 반영
- 26개 노드, 47개 관계선, FRED 실시간 데이터 연동 (v4.2)
- 주요 기능: 오르면?/내리면? 시뮬레이션, 레벨별 탐색, 카테고리 필터, 검색, 편집 모드
- 최근: 기대인플레이션/실질금리 추가, GDP→금리 오류 수정, 접근성/성능 개선, 에러 처리

## 남은 작업
- [ ] URL 파라미터 (?focus=nodeId)
- [ ] 범례 개선
- [ ] Phase 2: AI 연동, 대시보드 연동, 커스텀 노드, 이벤트/시나리오

## 구글 드라이브
- 엑셀로 데이터 기준 문서 관리 중
- 코드 변경 시 관련 엑셀도 즉시 동기화 (묻지 않고 반영)

## 작업 규칙
- 지시한 범위만 수정. 추가 적용 필요하면 먼저 물어볼 것
- 한국어로 소통, 기술 용어는 쉽게 설명
- 실행 명령어는 코드 블록으로 제공
