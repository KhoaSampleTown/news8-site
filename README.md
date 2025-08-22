# News 6-section Site (RSS + ChatGPT Summaries)

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill OPENAI_API_KEY
export $(cat .env | xargs)    # or use direnv
python collector.py           # builds data/<today>/*.json + latest.json
python summarize.py           # builds data/<today>/summaries.json and updates latest.json
python -m http.server 8080    # open http://localhost:8080/web/
```
> Run from project root so `/data` and `/web` are both served.

## Schedule
- Run `python run_cycle.py` for APScheduler (default every 3h), or set up a cron.

## Deploy on Fly.io
- `fly launch` then `fly deploy` (needs Fly CLI). Container serves `/web` and `/data` statically.
