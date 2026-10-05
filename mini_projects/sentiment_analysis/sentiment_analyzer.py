"""
Sentiment analysis tool using VADER (Valence Aware Dictionary and sEntiment Reasoner).

VADER is rule-based and specifically tuned for social-media text, making it ideal
for short, informal sentences without requiring a trained ML model.
"""

from dataclasses import dataclass
from typing import Literal

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


@dataclass
class SentimentResult:
    text: str
    positive: float
    neutral: float
    negative: float
    compound: float
    label: Literal["positive", "neutral", "negative"]

    def __str__(self) -> str:
        return (
            f"Text     : {self.text!r}\n"
            f"Label    : {self.label}\n"
            f"Compound : {self.compound:+.4f}\n"
            f"Scores   : pos={self.positive:.4f}  neu={self.neutral:.4f}  neg={self.negative:.4f}"
        )


def _label(compound: float) -> Literal["positive", "neutral", "negative"]:
    # Thresholds recommended by the VADER authors.
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


class SentimentAnalyzer:
    """Thin wrapper around VaderSentiment that returns structured results."""

    def __init__(self) -> None:
        self._analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> SentimentResult:
        if not text or not text.strip():
            raise ValueError("text must be a non-empty string")
        scores = self._analyzer.polarity_scores(text)
        return SentimentResult(
            text=text,
            positive=scores["pos"],
            neutral=scores["neu"],
            negative=scores["neg"],
            compound=scores["compound"],
            label=_label(scores["compound"]),
        )

    def analyze_batch(self, texts: list[str]) -> list[SentimentResult]:
        return [self.analyze(t) for t in texts]


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _demo() -> None:
    samples = [
        "I absolutely love this product! It's amazing.",
        "This is the worst experience I've ever had.",
        "The package arrived on time.",
        "Not bad, but could be better.",
        "Absolutely fantastic service! Highly recommend 😊",
        "I hate waiting. This is so frustrating!!!",
    ]

    analyzer = SentimentAnalyzer()
    print("=" * 60)
    print("Sentiment Analysis Demo")
    print("=" * 60)
    for result in analyzer.analyze_batch(samples):
        print(result)
        print("-" * 60)


if __name__ == "__main__":
    _demo()
