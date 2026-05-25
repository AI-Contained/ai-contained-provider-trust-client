import pytest
from fastmcp import FastMCP

from ai_contained.provider.trust_client import register


@pytest.fixture
def mcp() -> FastMCP:
    server = FastMCP("test")
    register(server)
    return server
