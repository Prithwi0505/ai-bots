"""
FastAPI Main Application

Entry point for the multi-bot AI system.
All queries are auto-routed — no manual bot selection endpoints.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import classifier

app = FastAPI(
    title="Integrated Bots – Gemini-Powered Multi-Bot AI System",
    description=(
        "A unified REST API that auto-routes user queries to specialized bots "
        "(Banking, Cooking, Finance, GenZ Content, GPT Master) using Google Gemini."
    ),
    version="2.0.0",
)

# ── CORS (allow all origins for development) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include the single auto-router ──────────────────────────────
app.include_router(classifier.router)      # /chat

# ── Static Files ────────────────────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "Integrated Bots API is running — all queries are auto-routed via POST /chat",
        "docs": "/docs",
        "ui": "/ui",
    }


@app.get("/ui", tags=["Frontend"])
async def serve_ui():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
