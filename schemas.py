"""
Pydantic models for request / response payloads.

Only the auto-routed chat flow remains.
"""

from pydantic import BaseModel, Field


# ─── Request ────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User query text")


# ─── Response ───────────────────────────────────────────────────

class RoutedResponse(BaseModel):
    bot: str = Field(..., description="Bot that handled the query")
    reply: str = Field(..., description="Bot response text")
    routed_to: str = Field(..., description="Bot label the query was routed to")
