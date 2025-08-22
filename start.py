# start.py — serve web + run daily job at 08:00 GMT+7
import threading, os, time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from server import app         # aiohttp app
import collector, summarize

def job():
    print('[JOB] start')
    raw = collector.collect_raw()
    collector.route_and_write(raw)
    summarize.main()
    print('[JOB] done')

def start_scheduler():
    # chạy ngay 1 lần khi container khởi động
    job()
    # 08:00 Asia/Ho_Chi_Minh (GMT+7)
    tz = 'Asia/Ho_Chi_Minh'
    sched = BackgroundScheduler(timezone=tz)
    trigger = CronTrigger(hour=8, minute=0, timezone=tz)
    sched.add_job(job, trigger, id='collect_summarize', coalesce=True, max_instances=1, replace_existing=True)
    sched.start()
    while True:
        time.sleep(3600)

def start_web():
    from aiohttp import web
    web.run_app(app, port=8080)

if __name__ == '__main__':
    t1 = threading.Thread(target=start_scheduler, daemon=True)
    t1.start()
    start_web()  # foreground
