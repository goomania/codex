"""MCP server used by the classroom demo."""

from __future__ import annotations

from typing import Any

from mcp import types
from mcp.server import Server

from .knowledge_base import TopicSummary, get_topic, list_topics


def _tool_list_topics() -> types.Tool:
    return types.Tool(
        name="list_topics",
        title="List classroom topics",
        description="Return the list of study topics the tutor knows about.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
        outputSchema={
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Names of available topics.",
                }
            },
            "required": ["topics"],
            "additionalProperties": False,
        },
    )


def _tool_topic_summary() -> types.Tool:
    return types.Tool(
        name="get_topic_summary",
        title="Explain a topic",
        description="Look up a short explanation and study tip for a topic.",
        inputSchema={
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic name as returned by list_topics.",
                }
            },
            "required": ["topic"],
            "additionalProperties": False,
        },
        outputSchema={
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "summary": {"type": "string"},
                "difficulty": {
                    "type": "string",
                    "enum": ["intro", "intermediate"],
                },
                "study_tip": {"type": "string"},
            },
            "required": ["topic", "summary", "difficulty", "study_tip"],
            "additionalProperties": False,
        },
    )


def create_demo_server() -> Server:
    """Create a configured MCP server exposing classroom tutor tools."""

    server = Server(
        name="Classroom Tutor",
        instructions=(
            "You are connected to a classroom tutor service. Use the available tools to explore "
            "topics and retrieve helpful study tips for students."
        ),
    )

    tools = [_tool_list_topics(), _tool_topic_summary()]

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        return tools

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any]) -> tuple[list[types.TextContent], dict[str, Any]] | dict[str, Any]:
        if name == "list_topics":
            return {
                "topics": list_topics(),
            }

        if name == "get_topic_summary":
            topic_name = arguments.get("topic", "")
            topic: TopicSummary = get_topic(topic_name)
            structured = {
                "topic": topic.title,
                "summary": topic.summary,
                "difficulty": topic.difficulty,
                "study_tip": topic.study_tip,
            }
            message = types.TextContent(
                type="text",
                text=(
                    f"Topic: {topic.title}\n"
                    f"Summary: {topic.summary}\n"
                    f"Study tip: {topic.study_tip}"
                ),
            )
            return ([message], structured)

        raise ValueError(f"Unknown tool requested: {name}")

    return server
