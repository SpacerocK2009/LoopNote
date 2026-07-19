from __future__ import annotations

import threading
import webbrowser
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database import initialize_database
from backend.routes.api import router
from backend.services.image_service import CURRENT_DIR, ensure_image_directories

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    ensure_image_directories()
    yield


app = FastAPI(title="LoopNote — A Desktop Practice Companion", docs_url="/api/docs", lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/media/current", StaticFiles(directory=CURRENT_DIR, check_dir=False), name="media")


if __name__ == "__main__":
    from backend.desktop.runtime import DesktopRuntime, set_runtime

    runtime = DesktopRuntime()
    set_runtime(runtime)
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="info"))
    threading.Thread(target=server.run, name="local-web-server", daemon=True).start()
    if "--background" not in sys.argv:
        threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:8765")).start()
    try:
        runtime.run()
    finally:
        set_runtime(None)
        server.should_exit = True
