"""
Auto-Router — the single /chat endpoint that routes every query
to the correct bot automatically.

Uses Gemini LLM classification to decide which specialist bot handles each query.
"""

import re
from fastapi import APIRouter

from gemini_helpers import gemini_text
from schemas import ChatRequest, RoutedResponse

# Import answer functions from sibling modules
from routers.banking import banking_answer
from routers.cooking import cooking_answer
from routers.finance import finance_answer
from routers.gpt_master import gpt_master_answer
from routers.genz import genz_bot_org

router = APIRouter(tags=["Auto-Router"])


# ─── Bot Classifier ─────────────────────────────────────────────

ALLOWED_BOTS = {"banking", "cooking", "finance", "genz", "gpt_master", "unknown"}


def classify_bot(user_query: str) -> str:
    """Use Gemini to classify which bot should handle the user query."""
    instruction = """
You are a router for a unified assistant.

Bots:
- banking
- cooking
- finance
- genz
- gpt_master

Return ONLY one lowercase word.
"""
    raw = gemini_text(instruction + f"\nUser query: {user_query}")
    label = (raw or "").lower().strip()
    label = re.sub(r"[^a-z_]", "", label)
    return label if label in ALLOWED_BOTS else "unknown"


# ─── Detailed script detection ──────────────────────────────────

def is_detailed_script_request(query: str) -> bool:
    keywords = [
        "platform", "duration", "script", "camera", "gesture", "hashtags",
        "reel", "tiktok", "youtube", "linkedin", "voiceover", "dialogue",
        "tutorial", "comedy", "listicle",
    ]
    q = query.lower()
    return sum(1 for k in keywords if k in q) >= 2 or "script" in q


# ─── Endpoint ───────────────────────────────────────────────────

@router.post("/chat", response_model=RoutedResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Auto-routed chat — the sole entry point for all user queries:
    1. classify_bot() decides which bot to use
    2. Dispatches to the matching answer function
    3. Returns the bot label + reply
    """
    bot = classify_bot(req.query)

    if bot == "banking":
        reply = banking_answer(req.query)
    elif bot == "cooking":
        reply = cooking_answer(req.query)
    elif bot == "finance":
        reply = finance_answer(req.query)
    elif bot == "genz":
        reply_txt, _ = genz_bot_org(req.query)
        reply = reply_txt
    elif bot == "gpt_master":
        reply = gpt_master_answer(req.query)
    else:
        reply = "Please rephrase your question clearly."

    return RoutedResponse(bot=bot, reply=reply, routed_to=bot)
