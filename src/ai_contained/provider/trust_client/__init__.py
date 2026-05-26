"""Trust client provider for AI-Contained."""

import os

import httpx
from fastmcp import FastMCP

from ai_contained.trust.client.trust_config import HttpClientFactory, init_trust_config


async def register(mcp: FastMCP, *, _http_client_factory: HttpClientFactory | None = None) -> None:
    """Register the trust client with the MCP server.

    Reads TRUST_SERVERS and blocks until all trust server connections are established.
    After register() returns, get_trust_config() is live and ready for use.
    """
    factory = _http_client_factory or (lambda url: httpx.AsyncClient(base_url=url))
    await init_trust_config(os.environ.get("TRUST_SERVERS", ""), factory)
