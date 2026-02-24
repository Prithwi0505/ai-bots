"""
Centralized configuration — loads .env and exposes all keys / constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the parent project (integrated_bots/.env) or local .env
_env_candidates = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parent.parent / "integrated_bots" / ".env",
]
for _p in _env_candidates:
    if _p.exists():
        load_dotenv(_p)
        break

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY missing in .env file")

# Gemini models in fallback order (same as original)
GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

# Wikipedia REST API (no key needed)
WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/"
WIKI_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKI_HEADERS = {"User-Agent": "GenZContentBot/1.0 (contact: your-email@example.com)"}
