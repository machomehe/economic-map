#!/usr/bin/env python3
"""경제 지표 관계도용 FRED 데이터 수집"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

FRED_API_KEY = os.environ.get('FRED_API_KEY', '')

# data/data.json의 dataSource.fred 기준
SERIES_IDS = [
    'FEDFUNDS',         # us_rate: 기준금리
    'DFII10',           # us_realrate: 실질금리 (10Y TIPS)
    'A191RL1Q225SBEA',  # us_gdp: GDP 성장률
    'UNRATE',           # us_unemployment: 실업률
    'CPIAUCSL',         # us_cpi: 인플레이션 (CPI)
    'DCOILWTICO',       # us_oil: 유가 (WTI)
    'DGS10',            # us_bond: 국채금리 (10Y)
    'T10Y2Y',           # us_spread: 장단기금리차
    'BAMLH0A0HYM2',    # us_hy: 하이일드 스프레드
    'NASDAQCOM',        # us_nasdaq: 나스닥 (성장주)
    'DTWEXBGS',         # us_dollar: 달러인덱스
    'VIXCLS',           # us_vix: VIX
    'CSUSHPISA',        # us_realestate: Case-Shiller 주택가격지수
    'GOLDAMGBD228NLBM', # us_commodity: 금 가격 (London Gold Fixing)
    'M2SL',             # us_m2: M2 통화량
    'UMCSENT',          # us_sentiment: 미시간대 소비자심리지수
    'WALCL',            # us_liquidity: 연준 총자산
    'GFDEBTN',          # us_fiscal: 미국 국가부채
    'DFF',              # us_cash: 실효 연방기금금리
    'RSAFS',            # kr_consumption: 소비 (소매판매, US proxy)
    'DEXKOUS',          # kr_won: 원/달러 환율
    'USEPUINDXD',       # us_tariff: 경제정책 불확실성
    'OVXCLS',           # us_war: 원유변동성지수 (OVX)
    'PAYEMS',           # us_nfp: 비농업고용
    'CIVPART',          # us_lfpr: 경제활동참가율
    'NAPM',             # us_pmi: 제조업 PMI (ISM Manufacturing)
    'T5YIE',            # us_expinf: 기대인플레이션 (5Y Breakeven)
    'ICSA',             # us_claims: 초기실업수당 청구건수
    'PCOPPUSDM',        # us_copper: 구리 가격 (월간)
    'NFCI',             # us_nfci: 시카고 연준 금융상황지수 (National Financial Conditions Index)
    'PCEPILFE',         # us_pce: Core PCE 물가지수 (연준 공식 타겟)
    'CES0500000003',    # us_wage: 평균시간당임금 (Average Hourly Earnings)
    'DEXJPUS',          # us_jpyusd: 엔/달러 환율
]

# Stock형 지표: 절대 수준보다 YoY% 변화가 의미있는 시리즈
YOY_SERIES = {
    'CPIAUCSL',         # CPI → YoY%
    'M2SL',             # M2 → YoY%
    'CSUSHPISA',        # Case-Shiller → YoY%
    'WALCL',            # 연준 대차대조표 → YoY%
    'GFDEBTN',          # 국가부채 → YoY%
    'RSAFS',            # 소매판매 → YoY%
    'PAYEMS',           # 비농업고용 → YoY%
    'PCEPILFE',         # Core PCE → YoY%
    'CES0500000003',    # 임금 → YoY%
}

# 데이터 빈도: 월간 통일을 위한 메타데이터
DAILY_SERIES = {
    'FEDFUNDS', 'DFII10', 'DCOILWTICO', 'DGS10', 'BAMLH0A0HYM2',
    'NASDAQCOM', 'DTWEXBGS', 'VIXCLS', 'GOLDAMGBD228NLBM', 'DFF',
    'USEPUINDXD', 'OVXCLS', 'T5YIE', 'DEXKOUS', 'DEXJPUS', 'NFCI',
}

WEEKLY_SERIES = {
    'ICSA', 'WALCL',
}

QUARTERLY_SERIES = {
    'A191RL1Q225SBEA', 'GFDEBTN',
}


def get_limit(series_id):
    """Get appropriate limit to fetch ~5 years of data."""
    if series_id in DAILY_SERIES:
        return 1300  # ~5 years of trading days
    elif series_id in WEEKLY_SERIES:
        return 260   # ~5 years of weeks
    elif series_id in QUARTERLY_SERIES:
        return 20    # ~5 years of quarters
    else:
        return 60    # ~5 years of months


def fetch_series(series_id, limit=120):
    params = urllib.parse.urlencode({
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': limit,
    })
    url = 'https://api.stlouisfed.org/fred/series/observations?' + params
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            if 'error_message' in data:
                print(f'  ERROR {series_id}: {data["error_message"]}')
                return []
            obs = data.get('observations', [])
            return [{'date': o['date'], 'value': o['value']}
                    for o in obs if o['value'] != '.']
    except Exception as e:
        print(f'  FAILED {series_id}: {e}')
        return []


def calc_yoy_pct(series):
    """Stock형 시리즈를 YoY% 변화율로 변환. 입력: 날짜 내림차순 리스트."""
    if len(series) < 2:
        return series

    # 날짜순 정렬 (오래된→최근)
    chrono = sorted(series, key=lambda x: x['date'])
    result = []

    for i, obs in enumerate(chrono):
        dt = datetime.strptime(obs['date'], '%Y-%m-%d')
        target = dt - timedelta(days=365)

        # 약 12개월 전 데이터 찾기
        best = None
        best_diff = float('inf')
        for j in range(i):
            jdt = datetime.strptime(chrono[j]['date'], '%Y-%m-%d')
            diff = abs((jdt - target).days)
            if diff < best_diff:
                best_diff = diff
                best = chrono[j]

        if best and best_diff < 90:  # 3개월 이내 허용
            old_val = float(best['value'])
            new_val = float(obs['value'])
            if old_val != 0:
                yoy = ((new_val - old_val) / abs(old_val)) * 100
                result.append({'date': obs['date'], 'value': str(round(yoy, 2))})

    # 다시 내림차순으로
    result.sort(key=lambda x: x['date'], reverse=True)
    return result


def fetch_series_meta(series_id):
    """FRED 시리즈 메타데이터 조회 (release_id, last_updated, frequency, title)."""
    params = urllib.parse.urlencode({
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
    })
    url = 'https://api.stlouisfed.org/fred/series?' + params
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            seriess = data.get('seriess', [])
            if not seriess:
                return None
            s = seriess[0]
            return {
                'title': s.get('title', ''),
                'frequency': s.get('frequency', ''),
                'last_updated': s.get('last_updated', ''),
                'observation_start': s.get('observation_start', ''),
                'observation_end': s.get('observation_end', ''),
            }
    except Exception as e:
        print(f'  META FAILED {series_id}: {e}')
        return None


def fetch_upcoming_releases(release_id, from_date):
    """FRED release/dates 엔드포인트에서 실제 예정된 발표일 조회.
    from_date: YYYY-MM-DD (오늘 기준 이후만 반환)"""
    params = urllib.parse.urlencode({
        'release_id': release_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'asc',
        'limit': 10,
        'include_release_dates_with_no_data': 'true',
    })
    url = 'https://api.stlouisfed.org/fred/release/dates?' + params
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            dates = data.get('release_dates', [])
            # 오늘 이후 날짜만 필터
            upcoming = [d['date'] for d in dates if d.get('date', '') >= from_date]
            return upcoming[:5]  # 최대 5개
    except Exception as e:
        print(f'  UPCOMING FAILED {release_id}: {e}')
        return []


def fetch_series_release_id(series_id):
    """시리즈가 속한 release_id 조회."""
    params = urllib.parse.urlencode({
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
    })
    url = 'https://api.stlouisfed.org/fred/series/release?' + params
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read())
            releases = data.get('releases', [])
            if releases:
                return releases[0].get('id')
    except Exception as e:
        print(f'  RELEASE_ID FAILED {series_id}: {e}')
    return None


def resample_to_monthly(series):
    """Convert any frequency to monthly (last value per month)."""
    if not series:
        return series

    # series comes in descending order from FRED
    # Take the first (most recent) observation per year-month
    seen = set()
    result = []
    for obs in series:
        ym = obs['date'][:7]  # "2025-03"
        if ym not in seen:
            seen.add(ym)
            result.append(obs)

    # Limit to 60 months (5 years)
    return result[:60]


def main():
    if not FRED_API_KEY:
        print('FRED_API_KEY not set')
        return

    result = {}
    for sid in SERIES_IDS:
        print(f'Fetching {sid}...')
        lim = get_limit(sid)
        raw = fetch_series(sid, limit=lim)
        if sid in YOY_SERIES and raw:
            yoy = calc_yoy_pct(raw)
            print(f'  → YoY% 변환: {len(raw)}건 → {len(yoy)}건')
            result[sid] = resample_to_monthly(yoy)
        else:
            result[sid] = resample_to_monthly(raw)
        print(f'  → 월간 {len(result[sid])}건')

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'data': result,
    }

    os.makedirs('data', exist_ok=True)
    with open('data/values.json', 'w') as f:
        json.dump(output, f, separators=(',', ':'))

    print(f'Done. data/values.json updated at {output["updated"]}')

    # ==========================================
    # releases.json 생성 (실데이터만)
    # ==========================================
    print('\n=== Fetching release metadata ===')
    from datetime import date
    today = date.today().isoformat()

    releases_data = []
    release_id_cache = {}  # release_id → upcoming dates (중복 호출 방지)

    for sid in SERIES_IDS:
        meta = fetch_series_meta(sid)
        if not meta:
            continue

        # 이전값/최신값은 이미 result에 있음
        series_values = result.get(sid, [])
        last_val = series_values[0]['value'] if series_values else None
        prev_val = series_values[1]['value'] if len(series_values) > 1 else None

        # 3개월 평균 (월간 기준 첫 3개)
        try:
            recent = [float(v['value']) for v in series_values[:3]]
            avg_3m = round(sum(recent) / len(recent), 2) if recent else None
        except:
            avg_3m = None

        # 향후 발표일 (FRED 공식)
        rid = fetch_series_release_id(sid)
        upcoming = []
        if rid:
            if rid not in release_id_cache:
                release_id_cache[rid] = fetch_upcoming_releases(rid, today)
            upcoming = release_id_cache[rid]

        releases_data.append({
            'seriesId': sid,
            'title': meta['title'],
            'frequency': meta['frequency'],
            'lastUpdated': meta['last_updated'],
            'lastValue': last_val,
            'previousValue': prev_val,
            'avg3m': avg_3m,
            'releaseId': rid,
            'upcomingDates': upcoming,
        })
        print(f'  {sid}: last={meta["last_updated"][:10] if meta["last_updated"] else "N/A"}, upcoming={len(upcoming)}')

    # Fed 공식 2026 FOMC 일정 (federalreserve.gov 공식)
    fomc_2026 = [
        '2026-01-27', '2026-01-28',
        '2026-03-17', '2026-03-18',
        '2026-04-28', '2026-04-29',
        '2026-06-16', '2026-06-17',
        '2026-07-28', '2026-07-29',
        '2026-09-15', '2026-09-16',
        '2026-11-03', '2026-11-04',
        '2026-12-15', '2026-12-16',
    ]
    fomc_upcoming = [d for d in fomc_2026 if d >= today]

    releases_output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'source': 'FRED API (series release_dates) + Fed 공식 FOMC 일정',
        'disclaimer': '추측 데이터 없음. 모든 날짜와 수치는 FRED/Fed 공식 발표 기준.',
        'releases': releases_data,
        'fomc2026': fomc_upcoming,
    }

    with open('data/releases.json', 'w') as f:
        json.dump(releases_output, f, ensure_ascii=False, indent=2)
    print(f'\nDone. data/releases.json updated at {releases_output["updated"]}')

if __name__ == '__main__':
    main()
