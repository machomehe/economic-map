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
- Service Worker: sw.js (오프라인 캐시)

## 현재 상태 (2026-04-08)
- v5.0: 전문가 10인 피드백 기반 대규모 개선 (Phase 0~3 완료)
- 33개 노드, 77개 관계선, FRED 실시간 데이터 연동
- 주요 기능:
  - 오르면?/내리면? 가중전파 시뮬레이션 (감쇠, depth 3, 영향도%) + 복합 시나리오
  - 레벨별 탐색 (노드 크기 차등: L1×1.2, L2×1.0, L3×0.85)
  - 카테고리 필터, 검색, 편집 모드
  - 시차(lag)/인과·상관 태그 표시
  - 스파크라인 (80px, 시간축+호버 툴팁)
  - Two-tap 패턴 + long-press + 바텀시트 스와이프
  - URL 파라미터 (?focus=nodeId&sim=up&lv=2)
  - PNG 내보내기
  - Service Worker 오프라인 지원
  - CSP + innerHTML 제거 (보안 강화)
  - Safe Area 대응 (노치)
  - CSS Variables 기반 디자인 시스템
  - 면책 고지 표시
- 최근 추가 노드: 초기실업수당(ICSA), 구리(PCOPPUSDM)
- fetch_data.py: 120포인트 수집, YoY% 자동 변환 (CPI, M2 등 stock형), 금 가격(GOLDAMGBD228NLBM)

## 남은 작업 (별도 로드맵 — 아키텍처/비즈니스 변경 필요)
- [ ] 범례 개선
- [ ] fallback 데이터 소스 (서버사이드 프록시)
- [ ] 실시간 데이터 (WebSocket)
- [ ] 한국 시장 지표 (ECOS API)
- [ ] 알림/푸시 서버
- [ ] React/Vue 아키텍처 전환
- [ ] 뉴스 연동 (RSS 프록시)
- [ ] 포트폴리오 연동
- [ ] 커뮤니티/전문가
- [ ] 백테스팅, Sugiyama 레이아웃, 모바일 전용 뷰, 글로벌 시장, 아카이브

## 구글 드라이브
- 엑셀로 데이터 기준 문서 관리 중
- 코드 변경 시 관련 엑셀도 즉시 동기화 (묻지 않고 반영)

## 작업 규칙
- 지시한 범위만 수정. 추가 적용 필요하면 먼저 물어볼 것
- 한국어로 소통, 기술 용어는 쉽게 설명
- 실행 명령어는 코드 블록으로 제공
