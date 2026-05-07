"""
MEX Safety Agent — FastAPI Backend
MEX Engineering Group
"""

import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from routers import parse, review, export, library
from services.library_service import init_db
from auth import require_api_key
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="MEX Safety Agent",
    description="Machine safety compliance review system — MEX Engineering Group",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_auth = {"dependencies": [__import__("fastapi").Depends(require_api_key)]}
app.include_router(parse.router,   prefix="/api/parse",   tags=["Drawing Parser"],      **_auth)
app.include_router(review.router,  prefix="/api/review",  tags=["Compliance Review"],   **_auth)
app.include_router(export.router,  prefix="/api/export",  tags=["Redline Export"],      **_auth)
app.include_router(library.router, prefix="/api/library", tags=["Equipment Library"],   **_auth)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/review.html")
async def review_page():
    return FileResponse("static/review.html")

@app.get("/export.html")
async def export_page():
    return FileResponse("static/export.html")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "MEX Safety Agent"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("RAILWAY_ENVIRONMENT") is None  # no hot-reload in production
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)