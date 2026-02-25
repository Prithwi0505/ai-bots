"""
Finance Bot — answer logic only (no direct endpoint).

Called internally by the auto-router in classifier.py.
"""

from gemini_helpers import gemini_text

# ── Rules (identical to original) ────────────────────────────────
FINANCE_RULES = """\
You are a finance education assistant. Follow these rules strictly:
- Provide conceptual explanations ONLY.
- Do NOT give financial advice.
- No stock picks, no price targets, no buy/sell recommendations.
- If numbers are required, show formulas or clearly hypothetical examples, not predictions.
- ALWAYS include a short risk disclaimer at the end:
  "Disclaimer: This is educational information only, not financial advice."
- Prefer clear definitions and examples over opinions.
"""

FALLBACK_MSG = (
    "I can explain finance concepts like budgeting, interest, risk, diversification, "
    "compound interest, stocks, bonds, and basic investing principles.\n\n"
    "Disclaimer: This is educational information only, not financial advice."
)

DISCLAIMER = "\n\nDisclaimer: This is educational information only, not financial advice."


def _build_prompt(user_query: str) -> str:
    return (
        FINANCE_RULES
        + "\n\nUser question: "
        + user_query.strip()
        + "\n\nGive a concise conceptual explanation and then the disclaimer."
    )


def finance_answer(user_query: str) -> str:
    out = gemini_text(_build_prompt(user_query))
    if out:
        if "educational information only" not in out.lower():
            out += DISCLAIMER
        return out
    return FALLBACK_MSG
