"""
Pydantic models for all request / response payloads.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ─── Generic Chat ───────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query text")


class ChatResponse(BaseModel):
    bot: str = Field(..., description="Bot that handled the query")
    reply: str = Field(..., description="Bot response text")


# ─── Auto-routed Chat ──────────────────────────────────────────

class RoutedResponse(BaseModel):
    bot: str
    reply: str
    routed_to: str = Field(..., description="Bot label the query was routed to")


# ─── Classifier ─────────────────────────────────────────────────

class ClassifyRequest(BaseModel):
    query: str = Field(..., min_length=1)
    use_llm: bool = Field(False, description="Force LLM classification")


class ClassifyResponse(BaseModel):
    category: str
    bot: str
    confidence: str


# ─── GenZ Bot (detailed) ────────────────────────────────────────

class GenZRequest(BaseModel):
    query: str = Field(..., min_length=1)
    platform: str = Field("instagram_reel")
    duration: int = Field(30, ge=5, le=120)
    content_type: str = Field("script_voiceover")
    area_spec: str = Field("")
    location: str = Field("")
    language: str = Field("auto")
    tone: str = Field("genz")
    include_trending: bool = Field(True)
    deliver_camera_cues: bool = Field(True)
    compare_with_reels: bool = Field(True)


class GenZResponse(BaseModel):
    reply: str
    language_detected: str = Field("en")
