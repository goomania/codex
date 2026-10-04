import pytest

from mini_projects.sentiment_analysis.sentiment_analyzer import SentimentAnalyzer, SentimentResult


@pytest.fixture
def analyzer():
    return SentimentAnalyzer()


def test_positive_text(analyzer):
    result = analyzer.analyze("I absolutely love this! It's fantastic.")
    assert result.label == "positive"
    assert result.compound > 0.05


def test_negative_text(analyzer):
    result = analyzer.analyze("This is terrible and I hate it.")
    assert result.label == "negative"
    assert result.compound < -0.05


def test_neutral_text(analyzer):
    result = analyzer.analyze("The meeting is at 3pm.")
    assert result.label == "neutral"


def test_returns_sentiment_result(analyzer):
    result = analyzer.analyze("Great day!")
    assert isinstance(result, SentimentResult)
    assert result.text == "Great day!"
    assert 0.0 <= result.positive <= 1.0
    assert 0.0 <= result.neutral <= 1.0
    assert 0.0 <= result.negative <= 1.0
    assert -1.0 <= result.compound <= 1.0


def test_batch_analysis(analyzer):
    texts = ["I love it!", "Terrible.", "It is what it is."]
    results = analyzer.analyze_batch(texts)
    assert len(results) == 3
    assert results[0].label == "positive"
    assert results[1].label == "negative"


def test_empty_text_raises(analyzer):
    with pytest.raises(ValueError):
        analyzer.analyze("")


def test_whitespace_only_raises(analyzer):
    with pytest.raises(ValueError):
        analyzer.analyze("   ")


def test_emoji_positive(analyzer):
    result = analyzer.analyze("Best day ever 😊🎉")
    assert result.label == "positive"
