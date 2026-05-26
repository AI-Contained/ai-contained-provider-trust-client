"""End-to-end demonstration: trust client registers with a trust server and fetches an encrypted secret."""

import json
from collections.abc import AsyncGenerator

import httpx
import pytest
from assertpy import assert_that
from fastmcp import FastMCP
from fastmcp.client import Client
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ai_contained.trust import client as trust_client
from ai_contained.trust import server as trust_server


def describe_secret_route() -> None:
    expected_request = {"account": "my-aws-account"}
    expected_secret = {"access_key": "AKIAIOSFODNN7EXAMPLE", "secret_key": "wJalrXUtnFEMI"}

    @pytest.fixture
    async def trust_server_mcp() -> FastMCP:
        server = FastMCP("trust-server")
        # register() wires up /trust/register — the key-exchange endpoint.
        await trust_server.register(server)

        # secret_route() wraps a handler with signature verification + response encryption.
        # In production this would return real credentials (e.g. from AWS STS).
        @trust_server.secret_route(server, "aws")
        async def aws_secret(request: Request) -> Response:
            body = json.loads(await request.body())
            assert_that(body).is_equal_to(expected_request)
            return JSONResponse(expected_secret)

        return server

    @pytest.fixture
    async def http(trust_server_mcp: FastMCP) -> AsyncGenerator[httpx.AsyncClient, None]:
        # Route HTTP directly to the in-process trust server — no real network needed.
        transport = httpx.ASGITransport(app=trust_server_mcp.http_app(), client=("127.0.0.1", 50000))
        async with httpx.AsyncClient(transport=transport, base_url="http://ignored") as client:
            yield client

    async def it_posts_a_payload_and_receives_the_expected_secret(
        mcp: FastMCP, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TRUST_SERVERS", "aws=http://127.0.0.1:8080")
        # Entering the client lifespan triggers register() → init_trust_config() → key exchange with the trust server.
        async with Client(transport=mcp):
            result = await trust_client.get_trust_config().get_client("aws").post(expected_request)
            assert_that(result).is_equal_to(expected_secret)
