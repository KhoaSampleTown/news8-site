from aiohttp import web
import os

async def handle(request):
    path = request.match_info.get('path','web/index.html')
    if path in ('','/'): path='web/index.html'
    file_path=os.path.join('/app',path)
    if not os.path.exists(file_path):
        return web.Response(status=404,text='Not found')
    return web.FileResponse(file_path)

app = web.Application()
app.router.add_get('/{path:.*}', handle)

# --- admin refresh endpoint ---
import os, asyncio
from aiohttp import web
import collector, summarize

REFRESH_TOKEN = os.getenv("REFRESH_TOKEN", "changeme")

async def refresh_handler(request):
    token = request.query.get("token", "")
    if token != REFRESH_TOKEN:
        return web.Response(status=401, text="unauthorized")
    # chạy job đồng bộ (non-blocking HTTP)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_job)
    return web.Response(text="ok")

def run_job():
    print("[ADMIN] refresh start")
    raw = collector.collect_raw()
    collector.route_and_write(raw)
    summarize.main()
    print("[ADMIN] refresh done")

app.router.add_get("/admin/refresh", refresh_handler)


if __name__ == '__main__':
    web.run_app(app, port=8080)
