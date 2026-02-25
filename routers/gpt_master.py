"""
GPT Master Bot — answer logic only (no direct endpoint).

Called internally by the auto-router in classifier.py.
"""

from gemini_helpers import gemini_text

# ── Rules (identical to original) ────────────────────────────────
GPT_MASTER_RULES = """\
You are an AI mentor (GPT Master). Follow these rules:
- Explain concepts clearly and simply.
- Break down ideas step by step.
- Challenge weak assumptions gently.
- Do not hallucinate; admit uncertainty.
- Prefer reasoning over verbosity.
"""

FALLBACK_MSG = (
    "Let's break this down into a few steps:\n"
    "1) Clarify your goal in one sentence.\n"
    "2) List what you already know and what you're unsure about.\n"
    "3) Identify the next smallest action you can take in the next 24 hours.\n\n"
    "If you tell me your goal and what you've tried so far, "
    "I can help you organize your thinking more concretely."
)


def _build_prompt(user_query: str) -> str:
    return (
        GPT_MASTER_RULES
        + "\n\nUser request: "
        + user_query.strip()
        + "\n\nProvide a step-by-step, concise answer. If unsure, say so."
    )


def gpt_master_answer(user_query: str) -> str:
    out = gemini_text(_build_prompt(user_query))
    return out if out else FALLBACK_MSG
