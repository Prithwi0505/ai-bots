"""
Banking Bot Router — preserves all auth-trigger + Gemini logic from the original.
"""

from fastapi import APIRouter

from gemini_helpers import gemini_text
from schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/banking", tags=["Banking Bot"])

# ── Rules (identical to original) ────────────────────────────────
BANKING_RULES = """\
You are a banking support assistant. Follow these rules strictly:
- Answer ONLY banking-related FAQs.
- NEVER invent customer data.
- If a query would need account access or personal info, reply exactly: "Authentication required."
- Allowed topics: accounts, loans, cards, interest, KYC, fees.
- Forbidden: predictions, advice, jokes, opinions.
- Keep answers short, factual, neutral.
- If unsure → say "I don't have that information."
"""

AUTH_KEYWORDS = [
    "my balance", "my account", "my statement", "my card",
    "my loan", "transfer from my", "my transaction",
    "my limit", "my credit",
]


def _build_prompt(user_query: str) -> str:
    return (
        BANKING_RULES
        + "\n\nUser query: "
        + user_query.strip()
        + "\n\nRespond with a concise banking FAQ answer."
    )


def banking_answer(user_query: str) -> str:
    lower = user_query.lower()
    if any(k in lower for k in AUTH_KEYWORDS):
        return "Authentication required."
    out = gemini_text(_build_prompt(user_query))
    return out or "I don't have that information."


@router.post("", response_model=ChatResponse)
async def banking_endpoint(req: ChatRequest):
    reply = banking_answer(req.query)
    return ChatResponse(bot="banking", reply=reply)
