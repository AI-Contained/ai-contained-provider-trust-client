from collections.abc import AsyncGenerator

import httpx
import pytest
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response

from ai_contained.trust import server as trust_server
from ai_contained.trust.client.trust_config import reset_trust_config
from ai_contained.trust.server.trust_store import get_trust_store


async def _raise_not_implemented(request: Request) -> Response:
    raise NotImplementedError


class AwsSecretHandler:
    handle = _raise_not_implemented


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_trust_config()
    get_trust_store().reset()
    trust_server.get_trust_config().reset("127.0.0.1")


@pytest.fixture
def mcp() -> FastMCP:
    return FastMCP("test")


@pytest.fixture
async def trust_server_mcp() -> FastMCP:
    server = FastMCP("trust-server")
    await trust_server.register(server)

    @trust_server.secret_route(server, "aws")
    async def aws_secret(request: Request) -> Response:
        return await AwsSecretHandler.handle(request)

    return server


@pytest.fixture
async def http(trust_server_mcp: FastMCP) -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=trust_server_mcp.http_app(), client=("127.0.0.1", 50000))
    async with httpx.AsyncClient(transport=transport, base_url="http://ignored") as client:
        yield client
