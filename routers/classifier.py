"""
Classifier / Router — provides both standalone classification and auto-routed chat.

Preserves:
- Rule-based keyword scoring (classifier.py)
- Gemini LLM classification (classifier.py)
- Inline classifier from app.py (classify_bot)
- Hybrid routing: rules → Gemini → safe fallback
"""

import re
from fastapi import APIRouter

from gemini_helpers import gemini_text, gemini_json
from schemas import (
    ChatRequest,
    ChatResponse,
    ClassifyRequest,
    ClassifyResponse,
    RoutedResponse,
)

# Import answer functions from sibling routers
from routers.banking import banking_answer
from routers.cooking import cooking_answer
from routers.finance import finance_answer
from routers.gpt_master import gpt_master_answer
from routers.genz import genz_bot_org, handle_query as genz_handle_query

router = APIRouter(tags=["Classifier & Router"])


# ─── Rule-Based Keywords (from classifier.py) ───────────────────

KEYWORDS = {
    "cooking": [
        "recipe", "cook", "ingredients", "bake", "fry", "food", "dish",
        "kitchen", "meal", "cuisine",
    ],
    "banking": [
        "bank", "account", "credit card", "debit", "emi", "loan", "interest",
        "upi", "atm", "balance", "statement",
    ],
    "finance": [
        "invest", "stock", "mutual fund", "crypto", "tax", "saving",
        "salary", "budget", "insurance",
    ],
    "genz_content": [
        "reel", "post", "instagram", "linkedin", "tweet", "youtube",
        "shorts", "tiktok", "content", "viral", "hashtag",
    ],
}


def keyword_route(text: str):
    text = text.lower()
    scores = {k: 0 for k in KEYWORDS}
    for category, words in KEYWORDS.items():
        for w in words:
            if w in text:
                scores[category] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


# ─── Gemini LLM Classifier (from classifier.py) ─────────────────

def gemini_classify(text: str) -> dict:
    prompt = f"""
Classify the following user query into exactly ONE category.

Categories:
- cooking
- banking
- finance
- genz_content

Rules:
- Respond ONLY in valid JSON
- No explanation
- No markdown

User query:
{text}

Return format:
{{ "category": "<category>" }}
"""
    return gemini_json(prompt) or {}


# ─── Hybrid Router (from classifier.py) ─────────────────────────

def route_to_bot(user_input: str, use_llm: bool = False) -> dict:
    # 1️⃣ Rule-based (fast)
    rule_result = keyword_route(user_input)
    if rule_result and not use_llm:
        return {"category": rule_result, "bot": rule_result, "confidence": "medium"}

    # 2️⃣ Gemini LLM classifier
    llm_result = gemini_classify(user_input)
    category = llm_result.get("category")
    if category in KEYWORDS:
        return {"category": category, "bot": category, "confidence": "high"}

    # 3️⃣ Safe fallback
    return {"category": "finance", "bot": "finance", "confidence": "low"}


# ─── Inline Classifier (from app.py) ────────────────────────────

ALLOWED_BOTS = {"banking", "cooking", "finance", "genz", "gpt_master", "unknown"}


def classify_bot(user_query: str) -> str:
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


# ─── Detailed script detection (from app.py) ────────────────────

def is_detailed_script_request(query: str) -> bool:
    keywords = [
        "platform", "duration", "script", "camera", "gesture", "hashtags",
        "reel", "tiktok", "youtube", "linkedin", "voiceover", "dialogue",
        "tutorial", "comedy", "listicle",
    ]
    q = query.lower()
    return sum(1 for k in keywords if k in q) >= 2 or "script" in q


# ─── Endpoints ───────────────────────────────────────────────────

@router.post("/classify", response_model=ClassifyResponse)
async def classify_endpoint(req: ClassifyRequest):
    """Standalone classification — returns category + confidence only."""
    result = route_to_bot(req.query, use_llm=req.use_llm)
    return ClassifyResponse(**result)


@router.post("/chat", response_model=RoutedResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Auto-routed chat — mirrors the original Streamlit app.py logic:
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
        if is_detailed_script_request(req.query):
            reply_txt, _ = genz_bot_org(req.query)
        else:
            reply_txt, _ = genz_bot_org(req.query)
        reply = reply_txt
    elif bot == "gpt_master":
        reply = gpt_master_answer(req.query)
    else:
        reply = "Please rephrase your question clearly."

    return RoutedResponse(bot=bot, reply=reply, routed_to=bot)
