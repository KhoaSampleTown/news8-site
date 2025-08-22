from aiohttp import web
import os, asyncio
import collector, summarize

from dotenv import load_dotenv
load_dotenv(".env")


app = web.Application()

# --- admin refresh phải đăng ký TRƯỚC ---
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN", "changeme")

def run_job():
    print("[ADMIN] refresh start")
    raw = collector.collect_raw()
    collector.route_and_write(raw)
    summarize.main()
    print("[ADMIN] refresh done")

async def refresh_handler(request):
    token = request.query.get("token", "")
    if token != REFRESH_TOKEN:
        print("[ADMIN] unauthorized:", token)
        return web.Response(status=401, text="unauthorized")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_job)
    return web.Response(text="ok")

app.router.add_get("/admin/refresh", refresh_handler)

# --- file server để serve /web và /data ---
async def handle(request):
    path = request.match_info.get("path", "web/index.html")
    if path in ("", "/"): path = "web/index.html"
    file_path = os.path.join(os.getcwd(), path.lstrip("/"))
    if not os.path.exists(file_path):
        return web.Response(status=404, text="Not found")
    return web.FileResponse(file_path)

# route bắt‑mọi‑thứ đặt CUỐI CÙNG
app.router.add_get("/{path:.*}", handle)

if __name__ == "__main__":
    web.run_app(app, port=8080)
