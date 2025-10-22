"""Unit tests for the sentiment analysis helper functions."""

import pytest

from app import sentiment


def test_analyze_text_positive():
    result = sentiment.analyze_text("I absolutely love this stunning library!")
    assert result.label == "positive"
    assert result.score > 0
    assert result.positive > result.negative


def test_analyze_text_negative():
    result = sentiment.analyze_text("This is the worst experience I've ever had.")
    assert result.label == "negative"
    assert result.score < 0
    assert result.negative > result.positive


def test_analyze_text_rejects_empty():
    with pytest.raises(ValueError):
        sentiment.analyze_text("   ")
