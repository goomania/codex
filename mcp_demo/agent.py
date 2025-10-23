"""Rule-based classroom agent that talks to the MCP demo server."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from mcp.client.session import ClientSession

ALIASES = {
    "pythagoras": "Pythagorean theorem",
    "pythagorean": "Pythagorean theorem",
    "right triangle": "Pythagorean theorem",
    "newton": "Newton's laws of motion",
    "laws of motion": "Newton's laws of motion",
    "photosynthesis": "Photosynthesis",
    "respiration": "Cellular respiration",
}


@dataclass
class SimpleTutorAgent:
    """Tiny rule-based agent that relies on MCP tools for knowledge."""

    session: ClientSession
    _topics_cache: list[str] | None = field(default=None, init=False, repr=False)

    async def list_tool_names(self) -> list[str]:
        """Return the MCP tool names exposed by the server."""

        result = await self.session.list_tools()
        return [tool.name for tool in result.tools]

    async def _load_topics(self) -> list[str]:
        if self._topics_cache is None:
            call_result = await self.session.call_tool("list_topics", {})
            topics = call_result.structuredContent.get("topics") if call_result.structuredContent else None
            if isinstance(topics, list):
                self._topics_cache = [str(topic) for topic in topics]
            else:
                self._topics_cache = []
        return self._topics_cache

    def _match_topic(self, question: str, topics: Sequence[str]) -> str | None:
        normalized_question = question.lower()

        for alias, topic in ALIASES.items():
            if alias in normalized_question and topic in topics:
                return topic

        question_words = set(re.findall(r"[a-zA-Z']+", normalized_question))
        best_topic: str | None = None
        best_score = 0
        for topic in topics:
            topic_words = set(re.findall(r"[a-zA-Z']+", topic.lower()))
            score = len(question_words & topic_words)
            if topic.lower() in normalized_question:
                score += len(topic_words)
            if score > best_score:
                best_score = score
                best_topic = topic

        return best_topic if best_score > 0 else None

    async def answer(self, question: str) -> str:
        """Return a classroom-friendly answer for ``question``."""

        topics = await self._load_topics()
        topic = self._match_topic(question, topics)
        if topic is None:
            return (
                "I can help with introductory science and math topics like photosynthesis or the "
                "Pythagorean theorem. Try asking about one of those!"
            )

        call_result = await self.session.call_tool("get_topic_summary", {"topic": topic})
        if not call_result.structuredContent:
            return "Something went wrong—please try again."

        summary = str(call_result.structuredContent.get("summary", ""))
        tip = str(call_result.structuredContent.get("study_tip", ""))
        level = str(call_result.structuredContent.get("difficulty", "intro"))

        lines = [
            f"Here's a {level} explanation of {topic}:",
            summary,
        ]
        if tip:
            lines.append(f"Study tip: {tip}")
        return "\n".join(lines)
