"""Tests for agentic tool routing utilities."""

from app.agentic import calculate, run_agent


def test_calculate_expression():
    result = calculate("2 + 3 * 4")
    assert result.tool_name == "math.calculate"
    assert result.output.endswith("= 14.0")


def test_run_agent_sentiment_route():
    result = run_agent("sentiment: I love this product")
    assert result[0].tool_name == "nlp.sentiment"
    assert "Sentiment:" in result[0].output


def test_run_agent_default_help():
    result = run_agent("what can you do?")
    assert result[0].tool_name == "agent"
    assert "I can use tools" in result[0].output
