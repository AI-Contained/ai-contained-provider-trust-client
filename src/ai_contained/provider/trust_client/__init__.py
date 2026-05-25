"""Trust client provider for AI-Contained."""

import os
from collections.abc import AsyncIterator

from fastmcp import FastMCP
from fastmcp.server.lifespan import lifespan

from ai_contained.trust.client import init_trust_config


@lifespan
async def _trust_lifespan(server: FastMCP) -> AsyncIterator[None]:
    await init_trust_config(os.environ.get("TRUST_SERVERS", ""))
    yield


def register(mcp: FastMCP) -> None:
    """Register the trust client lifespan with the MCP server."""
    mcp._lifespan = _trust_lifespan
