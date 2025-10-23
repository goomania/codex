"""Helpers for running the MCP demo server and client inside the same process."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import anyio
from mcp.client.session import ClientSession
from mcp.server import Server
from mcp.shared.message import SessionMessage


@asynccontextmanager
async def connect_to_server(server: Server) -> AsyncIterator[ClientSession]:
    """Yield an initialized :class:`ClientSession` connected to ``server``.

    The helper spins up the MCP server in a background task and wires it to a
    client session using in-memory streams so the example stays self-contained.
    """

    client_to_server_send, client_to_server_recv = anyio.create_memory_object_stream[SessionMessage](0)
    server_to_client_send, server_to_client_recv = anyio.create_memory_object_stream[SessionMessage](0)

    initialization_options = server.create_initialization_options()

    async with anyio.create_task_group() as tg:
        tg.start_soon(
            server.run,
            client_to_server_recv,
            server_to_client_send,
            initialization_options,
            True,
        )

        async with ClientSession(server_to_client_recv, client_to_server_send) as session:
            await session.initialize()
            try:
                yield session
            finally:
                await client_to_server_send.aclose()

        tg.cancel_scope.cancel()
        await server_to_client_send.aclose()

