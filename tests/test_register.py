import httpx
import pytest
from assertpy import assert_that
from fastmcp import FastMCP

from ai_contained.trust import client as trust_client
from ai_contained.provider.trust_client import register


def describe_register() -> None:
    async def it_initializes_trust_config_on_startup(
        mcp: FastMCP, http: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TRUST_SERVERS", "http://127.0.0.1:8080")
        await register(mcp, _http_client_factory=lambda _: http)
        assert_that(trust_client.get_trust_config().get_client("aws")).is_instance_of(trust_client.TrustClient)

    async def it_initializes_empty_config_when_trust_servers_unset(
        mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("TRUST_SERVERS", raising=False)
        await register(mcp)
        assert_that(trust_client.get_trust_config().get_client("aws")).is_none()
