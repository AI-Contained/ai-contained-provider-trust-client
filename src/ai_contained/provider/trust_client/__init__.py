"""Trust client provider for AI-Contained."""

import os

from fastmcp import FastMCP

from ai_contained.trust.client import init_trust_config


async def register(mcp: FastMCP) -> None:
    """Register the trust client with the MCP server.

    Reads TRUST_SERVERS and blocks until all trust server connections are established.
    After register() returns, get_trust_config() is live and ready for use.
    """
    await init_trust_config(os.environ.get("TRUST_SERVERS", ""))
