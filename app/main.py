"""
FastAPI Application Entry Point
Multilingual Neural Translation Studio
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.routes import router as v1_router
from app.config import APP_SUBTITLE, APP_TITLE, APP_VERSION

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for model warm-up and resource teardown."""
    # Model initialization / warmup can be performed lazily or asynchronously here
    yield


app = FastAPI(
    title=APP_TITLE,
    description=APP_SUBTITLE,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local and web integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets & Templates
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include API v1 Router
app.include_router(v1_router)


@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
async def serve_index(request: Request):
    """Serves the main interactive Translation Studio web interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_title": APP_TITLE,
            "app_subtitle": APP_SUBTITLE,
            "version": APP_VERSION,
        },
    )


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
