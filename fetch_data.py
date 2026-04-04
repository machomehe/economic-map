#!/usr/bin/env python3
"""경제 지표 관계도용 FRED 데이터 수집"""
import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

FRED_API_KEY = os.environ.get('FRED_API_KEY', '')

# data/data.json의 dataSource.fred 기준
SERIES_IDS = [
    'FEDFUNDS',         # 기준금리
    'DFII10',           # 실질금리
    'A191RL1Q225SBEA',  # GDP 성장률
    'DGS10',            # 채권(10Y 금리)
    'T10Y2Y',           # 장단기금리차
    'BAMLH0A0HYM2',    # 하이일드 스프레드
    'CPIAUCSL',         # 인플레이션 (CPI)
    'RSAFS',            # 소비 (소매판매)
    'DTWEXBGS',         # 달러인덱스
    'DEXKOUS',          # 원/달러 환율
    'DCOILWTICO',       # 유가 (WTI)
    # 금: FRED 시리즈 비활성 — 추후 대체 소스 추가
    'UNRATE',           # 실업률
    'VIXCLS',           # VIX
    'NASDAQCOM',        # 나스닥 (성장주 proxy)
    'SP500',            # S&P 500
]

def fetch_series(series_id):
    params = urllib.parse.urlencode({
        'series_id': series_id,
        'api_key': FRED_API_KEY,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 10,
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

def main():
    if not FRED_API_KEY:
        print('FRED_API_KEY not set')
        return

    result = {}
    for sid in SERIES_IDS:
        print(f'Fetching {sid}...')
        result[sid] = fetch_series(sid)

    output = {
        'updated': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'data': result,
    }

    os.makedirs('data', exist_ok=True)
    with open('data/values.json', 'w') as f:
        json.dump(output, f, separators=(',', ':'))

    print(f'Done. data/values.json updated at {output["updated"]}')

if __name__ == '__main__':
    main()
