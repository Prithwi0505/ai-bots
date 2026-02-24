"""
Shared Gemini helpers — uses the new google.genai Client API.
Consolidates the duplicated gemini_text / gemini_json across every bot module.
"""

import json
import re
import logging
from typing import Optional

from google import genai

from config import GEMINI_API_KEY, GEMINI_MODELS

logger = logging.getLogger(__name__)

# Initialise client once at import time
client = genai.Client(api_key=GEMINI_API_KEY)


def _gemini_call(prompt: str, json_mode: bool = False) -> str:
    """
    Call Gemini with automatic model fallback.
    If json_mode=True, wraps prompt to coerce JSON-only output.
    """
    last_error = None
    for model_name in GEMINI_MODELS:
        try:
            if json_mode:
                prompt_wrapped = (
                    "Return ONLY valid JSON. Do not include markdown fences.\n"
                    + prompt
                )
                resp = client.models.generate_content(
                    model=model_name, contents=prompt_wrapped
                )
            else:
                resp = client.models.generate_content(
                    model=model_name, contents=prompt
                )
            text = (resp.text or "").strip()
            if text:
                return text
        except Exception as e:
            last_error = e
            logger.warning("Gemini model %s failed: %s", model_name, e)
            continue

    # If all models failed, return the error so the user sees it
    if last_error:
        return f"[Gemini API Error] {last_error}"
    return ""


def gemini_text(prompt: str) -> str:
    """Plain-text Gemini call with model fallback."""
    return _gemini_call(prompt, json_mode=False)


def gemini_json(prompt: str) -> Optional[dict]:
    """JSON Gemini call — returns parsed dict or None."""
    text = _gemini_call(prompt, json_mode=True)
    try:
        text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE)
        return json.loads(text)
    except Exception:
        return None
