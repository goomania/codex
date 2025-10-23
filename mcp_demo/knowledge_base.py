"""Simple knowledge base used by the classroom MCP demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TopicSummary:
    """Stores a short explanation and extra learning tips for a topic."""

    title: str
    summary: str
    difficulty: str
    study_tip: str


KNOWLEDGE_BASE: Dict[str, TopicSummary] = {
    "Photosynthesis": TopicSummary(
        title="Photosynthesis",
        summary=(
            "Photosynthesis is the process plants use to convert sunlight, water, and carbon dioxide "
            "into glucose (their food) and oxygen."
        ),
        difficulty="intro",
        study_tip="Remember the formula: sunlight + water + CO₂ -> glucose + O₂.",
    ),
    "Pythagorean theorem": TopicSummary(
        title="Pythagorean theorem",
        summary=(
            "In right triangles, the square of the hypotenuse equals the sum of the squares of the "
            "other two sides (a² + b² = c²)."
        ),
        difficulty="intro",
        study_tip="Draw a right triangle and square each side to visualize why the relationship works.",
    ),
    "Newton's laws of motion": TopicSummary(
        title="Newton's laws of motion",
        summary=(
            "Newton's three laws describe how forces affect motion: inertia, F = ma, and action/reaction."
        ),
        difficulty="intermediate",
        study_tip="Link each law to a real-life example like pushing a shopping cart or wearing a seat belt.",
    ),
    "Cellular respiration": TopicSummary(
        title="Cellular respiration",
        summary=(
            "Cells break down glucose in the presence of oxygen to produce ATP, releasing carbon dioxide "
            "and water as byproducts."
        ),
        difficulty="intermediate",
        study_tip="Compare it to photosynthesis—one stores energy, the other releases it.",
    ),
}


def list_topics() -> list[str]:
    """Return a sorted list of available topic titles."""

    return sorted(KNOWLEDGE_BASE)


def get_topic(topic: str) -> TopicSummary:
    """Retrieve details for a topic, raising ``KeyError`` if not found."""

    try:
        return KNOWLEDGE_BASE[topic]
    except KeyError as exc:  # pragma: no cover - defensive, but exercised in tests
        raise KeyError(f"Unknown topic: {topic}") from exc
