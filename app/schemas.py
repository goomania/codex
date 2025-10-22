"""Pydantic models for the HTTP API."""

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    """Payload accepted by ``POST /api/sentiment``."""

    text: str = Field(..., min_length=1, max_length=5_000, description="Text to analyse.")


class SentimentResponse(BaseModel):
    """Structured sentiment response returned to API clients."""

    label: str
    score: float
    positive: float
    neutral: float
    negative: float
