#!/usr/bin/env python3
import os, json, time, hashlib, re
import feedparser, requests
from collections import defaultdict
from dateutil import parser as du
from datetime import datetime
from urllib.parse import quote_plus
from config import GOOGLE_RSS, HL, GL, CEID, USER_AGENT, BROAD_QUERIES, RULES, THRESH

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9À-Ỹ])")

MAX_ITEMS_TOTAL = int(os.getenv('MAX_ITEMS_TOTAL', '250'))
MAX_ITEMS_PER_TOPIC = 80
OUT_DIR = os.getenv('OUT_DIR', 'data')

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip()

def summarize(text, k=2):
    s = norm(text)
    return "" if not s else " ".join(SENT_SPLIT.split(s)[:k])

def key_of(title, link):
    return hashlib.sha1((f"{title}\u241E{link}").encode("utf-8")).hexdigest()[:16]

def fetch_feed(url):
    try:
        r = requests.get(url, headers=USER_AGENT, timeout=20)
        r.raise_for_status()
        return feedparser.parse(r.content)
    except Exception as e:
        print("[WARN] feed fail", url, e)
        return None

def collect_raw():
    seen, raw = set(), []
    for q in BROAD_QUERIES:
        url = GOOGLE_RSS.format(q=quote_plus(q), hl=HL, gl=GL, ceid=CEID)
        feed = fetch_feed(url)
        if not feed:
            continue
        for e in feed.entries:
            title = norm(getattr(e, 'title', ''))
            link = norm(getattr(e, 'link', ''))
            if not title or not link:
                continue
            k = key_of(title, link)
            if k in seen:
                continue
            seen.add(k)
            summary = norm(getattr(e, 'summary', getattr(e, 'description', '')))
            published = getattr(e, 'published', getattr(e, 'updated', ''))
            try:
                ts = du.parse(published).isoformat()
            except Exception:
                ts = None
            raw.append({
                'id': k,
                'title': title,
                'link': link,
                'summary': summarize(summary),
                'published': ts,
            })
        time.sleep(0.6)
        if len(raw) >= MAX_ITEMS_TOTAL:
            break
    raw.sort(key=lambda x: x.get('published') or '', reverse=True)
    return raw

def tag_item(text):
    scores = defaultdict(int)
    for tag, rules in RULES.items():
        for rx, w in rules:
            if rx.search(text):
                scores[tag] += w
    return [t for t, s in scores.items() if s >= THRESH[t]]

def route_and_write(raw, out_dir=OUT_DIR):
    by_topic = defaultdict(list)
    for it in raw:
        text = (it['title'] + " \n " + (it.get('summary') or '')).lower()
        tags = tag_item(text)
        if not tags:
            continue
        for t in tags:
            by_topic[t].append(it)
    for t in by_topic:
        by_topic[t] = by_topic[t][:MAX_ITEMS_PER_TOPIC]

    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    day_dir = os.path.join(out_dir, date_str)
    os.makedirs(day_dir, exist_ok=True)

    idx = {"date": date_str, "topics": {}}
    for t, items in by_topic.items():
        path = os.path.join(day_dir, f"{t}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({"date": date_str, "topic": t, "items": items}, f, ensure_ascii=False, indent=2)
        idx["topics"][t] = {"count": len(items), "path": f"/data/{date_str}/{t}.json"}

    with open(os.path.join(out_dir, 'latest.json'), 'w', encoding='utf-8') as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    raw = collect_raw()
    route_and_write(raw)
