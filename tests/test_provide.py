import json
from collections.abc import AsyncGenerator

import httpx
import pytest
from assertpy import assert_that
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ai_contained.core.mcp import ProviderContext
from ai_contained.core.mcp.harness import Harness
from ai_contained.provider.trust_client import provide
from ai_contained.trust import client as trust_client
from ai_contained.trust import server as trust_server
from ai_contained.trust.server import TrustServer


async def _raise_not_implemented(request: Request) -> Response:
    raise NotImplementedError


class AwsSecretHandler:
    handle = _raise_not_implemented


@pytest.fixture
async def http() -> AsyncGenerator[httpx.AsyncClient, None]:
    """An in-process trust server whose /aws/secret route dispatches to AwsSecretHandler."""
    async with Harness(env={"TRUST_CLIENTS": "127.0.0.1"}) as h:
        trust = await h.install(trust_server.provide)
        assert isinstance(trust, TrustServer)

        @trust.secret_route(role="aws")
        async def aws_secret(request: Request) -> Response:
            return await AwsSecretHandler.handle(request)

        async with h.raw_client() as client:
            yield client


def describe_provide() -> None:
    async def it_returns_an_empty_config_when_trust_servers_is_unset() -> None:
        config = await provide(ProviderContext(FastMCP("test"), {}))
        assert_that(config.get_client("aws")).is_none()

    async def it_connects_and_returns_a_client_for_the_role(http: httpx.AsyncClient) -> None:
        ctx = ProviderContext(FastMCP("test"), {"TRUST_SERVERS": "http://127.0.0.1:8080"})
        config = await provide(ctx, _http_client_factory=lambda _: http)
        assert_that(config.get_client("aws")).is_instance_of(trust_client.TrustClient)

    async def it_posts_a_payload_and_receives_the_expected_secret(
        http: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        expected_request = {"account": "my-aws-account"}
        expected_secret = {"access_key": "AKIAIOSFODNN7EXAMPLE", "secret_key": "wJalrXUtnFEMI"}

        async def _handler(request: Request) -> Response:
            body = json.loads(await request.body())
            assert_that(body).is_equal_to(expected_request)
            return JSONResponse(expected_secret)

        monkeypatch.setattr(AwsSecretHandler, "handle", _handler)
        ctx = ProviderContext(FastMCP("test"), {"TRUST_SERVERS": "aws=http://127.0.0.1:8080"})
        config = await provide(ctx, _http_client_factory=lambda _: http)
        result = await config.get_client("aws").post(expected_request)
        assert_that(result).is_equal_to(expected_secret)

    async def it_fails_the_load_when_a_server_is_unreachable(monkeypatch: pytest.MonkeyPatch) -> None:
        # Fail-fast-at-boot: a bad TRUST_SERVERS must break provide(), not the
        # first credential request. Port 9 (discard) has no listener; skip the
        # retry backoff so the failure surfaces immediately.
        async def no_sleep(_: float) -> None:
            pass

        monkeypatch.setattr("ai_contained.trust.client.trust_config._sleep", no_sleep)
        ctx = ProviderContext(FastMCP("test"), {"TRUST_SERVERS": "aws=http://127.0.0.1:9"})
        with pytest.raises(httpx.ConnectError):
            await provide(ctx)
