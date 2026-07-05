"""Trust client provider for AI-Contained."""

import httpx

from ai_contained.core.mcp import ProviderContext
from ai_contained.trust.client import TrustConfig
from ai_contained.trust.client.trust_config import HttpClientFactory


async def provide(ctx: ProviderContext, *, _http_client_factory: HttpClientFactory | None = None) -> TrustConfig:
    """Read TRUST_SERVERS, connect to every trust server, and share the TrustConfig.

    Blocks (with retry/backoff) until every configured server has accepted
    our keys — an unreachable server fails the load, never the first request.
    Consumers fetch role clients from the state::

        trust = await ctx.ensure(trust_client.provide)
        client = trust.get_client("aws")
    """
    factory = _http_client_factory or (lambda url: httpx.AsyncClient(base_url=url))
    return await TrustConfig.create(ctx.environ.get("TRUST_SERVERS", ""), factory)
