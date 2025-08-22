#!/usr/bin/env python3
import os, json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


DATA_DIR = os.getenv('OUT_DIR', 'data')
MODEL = os.getenv('MODEL_NAME', 'gpt-4o-mini')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

SYSTEM = (
    "You are a bilingual (EN+VI) financial news summarizer for professional traders.\n"
    "- Input: a list of RSS headlines and/or summaries (they may already contain key figures).\n"
    "- Task: extract and retain ALL numerical data present in the input (yields, % changes, levels, bp, bn, $).\n"
    "- DO NOT invent numbers that are not explicitly in the input.\n"
    "- Output Vietnamese by default if input headlines are mixed EN/VI.\n"
    "- Style: 6–10 bullet points per section, one sentence each.\n"
    "- Each bullet must cite the figures explicitly mentioned in the input (if any) "
    "(e.g., 'UST10Y yield tăng 6bp lên 4.24%', 'GDP +2.9% y/y Q2', 'USD/VND 25,420 (+0.2% w/w)').\n"
    "- Close with one line of implication for traders or risk managers."
)


PROMPT_TMPL = (
    "Summarize the following headlines for the section '{topic}'. "
    "Group similar items, remove duplicates, avoid hype. If there are macro items (GDP, CPI, FDI, fiscal), "
    "tie them to bonds/FX/rates when relevant.\n\n"
    "HEADLINES JSON (title, summary, url):\n{payload}\n\n"
    "Return JSON with keys: section, bullets (array of strings), takeaway (string)."
)

TOPICS = {
    "fixedincome": "fixedincome.json",
    "equity": "equity.json",
    "commodity": "commodity.json",
    "cryptocurrency": "cryptocurrency.json",
    "exchangerate": "exchangerate.json",
    "interestrate": "interestrate.json"
}

def load_today_topic_files():
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    folder = os.path.join(DATA_DIR, date_str)
    files = {}
    for topic, filename in TOPICS.items():
        p = os.path.join(folder, filename)
        if os.path.exists(p):
            files[topic] = p
    return files

def summarize_topic(topic, path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    seen_titles = set()
    deduped = []
    for it in data.get('items', []):
        title = it.get('title', '').strip().lower()
        if title and title not in seen_titles:
            deduped.append(it)
            seen_titles.add(title)
    items = deduped[:80]
    lite = [{"title": it['title'], "summary": it.get('summary',''), "url": it['link']} for it in items]

    prompt = PROMPT_TMPL.format(topic=topic, payload=json.dumps(lite, ensure_ascii=False))
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role":"system","content": SYSTEM},
            {"role":"user","content": prompt}
        ]
    )
    txt = resp.choices[0].message.content
    if txt.strip().startswith("```json"):
        txt = txt.strip().removeprefix("```json").removesuffix("```").strip()

    try:
        obj = json.loads(txt)
    except Exception:
        obj = {"section": topic, "bullets": [txt], "takeaway": ""}
    return obj


def main():
    files = load_today_topic_files()
    out = {"date": datetime.utcnow().strftime('%Y-%m-%d'), "sections": {}}
    for topic, path in files.items():
        print("[SUM]", topic)
        out["sections"][topic] = summarize_topic(topic, path)

    day_dir = os.path.dirname(list(files.values())[0]) if files else os.path.join(DATA_DIR, datetime.utcnow().strftime('%Y-%m-%d'))
    os.makedirs(day_dir, exist_ok=True)
    with open(os.path.join(day_dir, 'summaries.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    latest_path = os.path.join(DATA_DIR, 'latest.json')
    if os.path.exists(latest_path):
        with open(latest_path, 'r', encoding='utf-8') as lf:
            latest = json.load(lf)
    else:
        latest = {"date": out['date'], "topics": {}}
    latest['summaries'] = {"path": f"/data/{out['date']}/summaries.json"}
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(latest, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
