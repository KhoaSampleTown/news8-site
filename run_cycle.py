#!/usr/bin/env python3
import os
from apscheduler.schedulers.blocking import BlockingScheduler
import collector, summarize

interval_minutes = int(os.getenv('RUN_EVERY_MIN', '180'))  # default 3h
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=interval_minutes)
def job():
    print('[JOB] start')
    raw = collector.collect_raw()
    collector.route_and_write(raw)
    summarize.main()
    print('[JOB] done')

if __name__ == '__main__':
    job()      # run once at start
    sched.start()
