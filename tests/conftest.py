from collections.abc import AsyncGenerator

import httpx
import pytest
from fastmcp import FastMCP

from ai_contained.trust import client as trust_client
from ai_contained.trust import server as trust_server
from ai_contained.trust.client.trust_config import reset_trust_config
from ai_contained.trust.server.trust_store import get_trust_store

from ai_contained.provider.trust_client import register


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_trust_config()
    get_trust_store().reset()
    trust_server.get_trust_config().reset("127.0.0.1")


@pytest.fixture
def trust_server_mcp() -> FastMCP:
    server = FastMCP("trust-server")
    trust_server.register(server)
    return server


@pytest.fixture
async def http(trust_server_mcp: FastMCP) -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=trust_server_mcp.http_app(), client=("127.0.0.1", 50000))
    async with httpx.AsyncClient(transport=transport, base_url="http://ignored") as client:
        yield client


@pytest.fixture(autouse=True)
def _patch_init_trust_config(http: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch) -> None:
    original = trust_client.init_trust_config

    async def _patched(raw: str, factory=None) -> trust_client.TrustConfig:
        return await original(raw, lambda url: http)

    monkeypatch.setattr("ai_contained.trust.client.trust_config.init_trust_config", _patched)
    monkeypatch.setattr("ai_contained.provider.trust_client.init_trust_config", _patched)


@pytest.fixture
def mcp() -> FastMCP:
    server = FastMCP("test")
    register(server)
    return server
