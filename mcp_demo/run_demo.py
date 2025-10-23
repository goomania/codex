"""Command-line entry point for the MCP classroom demo."""

from __future__ import annotations

import anyio

from .agent import SimpleTutorAgent
from .connection import connect_to_server
from .server import create_demo_server


async def main() -> None:
    server = create_demo_server()

    async with connect_to_server(server) as session:
        agent = SimpleTutorAgent(session)
        tool_names = await agent.list_tool_names()
        print("Connected tools:", ", ".join(tool_names))

        questions = [
            "Can you remind me what photosynthesis is?",
            "What do Newton's laws of motion say?",
            "Do you know anything about quantum field theory?",
        ]

        for question in questions:
            print("\nStudent:", question)
            answer = await agent.answer(question)
            print("Tutor:", answer)


if __name__ == "__main__":
    anyio.run(main)
