"""
FastAPI Main Application

Entry point for the multi-bot AI system.
Equivalent to the original integrated_bots/streamlit_frontend/app.py
but as a REST API server.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routers import banking, cooking, finance, gpt_master, genz, classifier

app = FastAPI(
    title="Integrated Bots – Gemini-Powered Multi-Bot AI System",
    description=(
        "A unified REST API that routes user queries to specialized bots "
        "(Banking, Cooking, Finance, GenZ Content, GPT Master) using Google Gemini."
    ),
    version="1.0.0",
)

# ── CORS (allow all origins for development) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ─────────────────────────────────────────────
app.include_router(classifier.router)      # /chat, /classify
app.include_router(banking.router)         # /banking
app.include_router(cooking.router)         # /cooking
app.include_router(finance.router)         # /finance
app.include_router(gpt_master.router)      # /gpt_master
app.include_router(genz.router)            # /genz, /genz/detailed

# ── Static Files (test frontend) ────────────────────────────────
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "message": "Integrated Bots API is running",
        "docs": "/docs",
        "ui": "/ui",
        "bots": ["banking", "cooking", "finance", "gpt_master", "genz"],
    }


@app.get("/ui", tags=["Frontend"])
async def serve_ui():
    """Serves the test frontend."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
