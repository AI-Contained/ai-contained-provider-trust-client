import pytest
from assertpy import assert_that
from fastmcp import FastMCP
from fastmcp.client import Client

from ai_contained.trust import client as trust_client


def describe_register() -> None:
    async def it_initializes_trust_config_on_startup(
        mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TRUST_SERVERS", "http://127.0.0.1:8080")
        async with Client(transport=mcp):
            assert_that(trust_client.get_trust_config()).is_not_none()
            assert_that(trust_client.get_trust_config().get_client("aws")).is_instance_of(trust_client.TrustClient)

    async def it_initializes_empty_config_when_trust_servers_unset(
        mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("TRUST_SERVERS", raising=False)
        async with Client(transport=mcp):
            assert_that(trust_client.get_trust_config()).is_not_none()
            assert_that(trust_client.get_trust_config().get_client("aws")).is_none()
