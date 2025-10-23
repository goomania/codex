from __future__ import annotations

import pytest

from mcp_demo import SimpleTutorAgent, connect_to_server, create_demo_server


pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


async def test_agent_answers_known_topic() -> None:
    server = create_demo_server()
    async with connect_to_server(server) as session:
        agent = SimpleTutorAgent(session)
        answer = await agent.answer("Can you explain the Pythagorean theorem?")

    assert "Pythagorean" in answer
    assert "Study tip" in answer


async def test_agent_handles_unknown_topic() -> None:
    server = create_demo_server()
    async with connect_to_server(server) as session:
        agent = SimpleTutorAgent(session)
        answer = await agent.answer("Tell me about quantum mechanics.")

    assert "introductory science and math" in answer


async def test_tool_listing_matches_server() -> None:
    server = create_demo_server()
    async with connect_to_server(server) as session:
        agent = SimpleTutorAgent(session)
        tools = await agent.list_tool_names()

    assert {"list_topics", "get_topic_summary"} <= set(tools)
