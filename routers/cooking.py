"""
Cooking Bot — answer logic only (no direct endpoint).

Called internally by the auto-router in classifier.py.
"""

from gemini_helpers import gemini_text

# ── Rules (identical to original) ────────────────────────────────
COOKING_RULES = """\
You are a cooking assistant. Always respond with:
1) Ingredients (with quantities)
2) Steps (numbered)
3) Cooking time

Rules:
- If the user doesn't give enough info, ask for the main ingredient or dish before giving a full recipe.
- Never include unsafe food practices.
- No storytelling.
- No nutrition claims unless clearly stated as estimates.
"""

FALLBACK_MSG = (
    "Please tell me the main ingredient or dish you want a recipe for "
    "(e.g., pasta, eggs, chicken, rice, salad, soup)."
)


def _build_prompt(user_query: str) -> str:
    return (
        COOKING_RULES
        + "\n\nUser request: "
        + user_query.strip()
        + "\n\nRespond ONLY with the required structure."
    )


def cooking_answer(user_query: str) -> str:
    if len(user_query.split()) < 2:
        return FALLBACK_MSG
    out = gemini_text(_build_prompt(user_query))
    return out if out else FALLBACK_MSG
