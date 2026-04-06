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
    'FEDFUNDS',         # us_rate: 기준금리
    'DFII10',           # us_real_rate: 실질금리 (10Y TIPS)
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
    'PPIACO',           # us_commodity: 생산자물가 원자재지수 (All Commodities)
    'M2SL',             # us_m2: M2 통화량
    'UMCSENT',          # us_sentiment: 미시간대 소비자심리지수
    'WALCL',            # us_liquidity: 연준 총자산 (글로벌 유동성 대용)
    'GFDEBTN',          # us_fiscal: 미국 국가부채
    'CD3M',             # us_cash: 3개월 CD 금리 (현금/예금 수익률 대용)
    'RSAFS',            # kr_consumption: 소비 (소매판매, US proxy)
    'DEXKOUS',          # kr_won: 원/달러 환율
    'USEPUINDXD',       # us_tariff: 경제정책 불확실성 (Economic Policy Uncertainty Index)
    'OVXCLS',           # us_war: 원유변동성지수 (OVX, 지정학 리스크 프록시)
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
