"""Sentiment analysis utilities built around the VADER lexicon."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

SentimentLabel = Literal["positive", "neutral", "negative"]


@dataclass(frozen=True)
class SentimentResult:
    """Structured sentiment classification output."""

    label: SentimentLabel
    score: float
    positive: float
    neutral: float
    negative: float


@lru_cache(maxsize=1)
def _get_analyzer() -> SentimentIntensityAnalyzer:
    """Return a cached ``SentimentIntensityAnalyzer`` instance.

    ``vaderSentiment`` is lightweight, but constructing the analyzer on each
    request is unnecessary overhead. Using :func:`functools.lru_cache` keeps a
    single instance around for the lifetime of the process.
    """

    return SentimentIntensityAnalyzer()


def _label_from_compound(compound: float, *, positive_threshold: float = 0.05, negative_threshold: float = -0.05) -> SentimentLabel:
    """Convert a VADER compound score to a discrete label.

    Args:
        compound: Compound sentiment score returned by VADER.
        positive_threshold: Upper bound for neutral classification.
        negative_threshold: Lower bound for neutral classification.

    Returns:
        One of ``"positive"``, ``"neutral"``, or ``"negative"``.
    """

    if compound >= positive_threshold:
        return "positive"
    if compound <= negative_threshold:
        return "negative"
    return "neutral"


def analyze_text(text: str) -> SentimentResult:
    """Analyze the provided text and return structured sentiment data."""

    if not text or not text.strip():
        raise ValueError("Text must not be empty.")

    analyzer = _get_analyzer()
    scores = analyzer.polarity_scores(text)
    label = _label_from_compound(scores["compound"])
    return SentimentResult(
        label=label,
        score=scores["compound"],
        positive=scores["pos"],
        neutral=scores["neu"],
        negative=scores["neg"],
    )
