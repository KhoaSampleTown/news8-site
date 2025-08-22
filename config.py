import os, re

LOCALE = os.getenv("APP_LOCALE", "en,US").split(",")  # [hl, gl]
HL, GL = (LOCALE + ["en", "US"])[:2]
CEID = f"{GL}:{'vi' if HL.startswith('vi') else 'en'}"

GOOGLE_RSS = "https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"
USER_AGENT = {"User-Agent": "News6/1.0 (+contact: you@example.com)"}

# Broad queries: markets + macro
BROAD_QUERIES = [
    # Markets
    'bond+yields', 'treasury+yields', 'government+bonds', 'yield+curve',
    'stock+market', 'equities', 'earnings', 'S%26P+500', 'VNINDEX',
    'Brent+crude', 'WTI+oil', 'gold+price', 'copper+price', 'LME',
    'bitcoin', 'ethereum', 'cryptocurrency+regulation', 'crypto+market',
    # Macro linkages
    'exchange+rate OR forex OR USD+VND OR EURUSD OR DXY',
    'interest+rate OR policy+rate OR interbank+rate OR OMO',
    'inflation OR CPI OR PPI',
    'GDP growth OR GDP+Việt+Nam OR GDP+Vietnam',
    'budget+deficit OR fiscal+deficit OR thu+chi+ngan+sach OR public+investment',
    'FDI OR exports OR imports OR trade+balance'
]

# Multi-label tagger rules
R = lambda p: re.compile(p, re.I)
RULES = {
    "fixedincome": [
        (R(r"\b(yield(s)?|UST|treasury|bond(s)?|gilt|bund|trái phiếu|trai phieu|auction)\b"), 2),
        (R(r"\b(yield\s*curve|duration|spread)\b"), 1),
        (R(r"\b(budget|fiscal|thu\s*chi\s*ngan\s*sach|ngân\s*sách|thâm\s*hụt|public\s*investment)\b"), 1),
    ],
    "equity": [
        (R(r"\b(stock|equit(y|ies)|earnings|IPO|VNINDEX|VN30|S&P\s*500|NASDAQ)\b"), 2),
    ],
    "commodity": [
        (R(r"\b(Brent|WTI|oil|gas|LNG|gold|silver|copper|iron ore|coal)\b"), 2),
    ],
    "cryptocurrency": [
        (R(r"\b(crypto|cryptocurrency|bitcoin|btc|ethereum|eth|stablecoin|defi)\b"), 2),
        (R(r"\b(SEC|ETF)\b"), 1),
    ],
    "exchangerate": [
        (R(r"\b(FX|forex|exchange\s*rate|t(ỷ|y)\s*gi(á|a)|usd/vnd|EURUSD|USDJPY|USDCNH|DXY|depreciation|appreciation)\b"), 2),
        (R(r"\b(export(s)?|import(s)?|trade\s*balance|FDI|remittance|xuất\s*khẩu|nhập\s*khẩu|cán\s*cân\s*thương\s*mai)\b"), 1),
    ],
    "interestrate": [
        (R(r"\b(interest\s*rate|policy\s*rate|interbank|OMO|SOFR|lãi\s*suất)\b"), 2),
        (R(r"\b(FOMC|Fed|ECB|BOE|BOJ|SBV|State\s*Bank\s*of\s*Vietnam)\b"), 1),
        (R(r"\b(deposit\s*rate|loan\s*rate|lãi\s*suất\s*huy(đ|\u0111)ộng|cho\s*vay|liên\s*ngân\s*hàng)\b"), 1),
    ],
}
THRESH = {k: 2 for k in RULES}

TOPIC_ORDER = ["fixedincome","equity","commodity","cryptocurrency","exchangerate","interestrate"]
