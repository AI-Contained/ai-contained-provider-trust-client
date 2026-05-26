"""End-to-end: trust client registers with a trust server and fetches an encrypted secret."""

import json

import httpx
import pytest
from assertpy import assert_that
from conftest import AwsSecretHandler
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from ai_contained.provider.trust_client import register
from ai_contained.trust import client as trust_client


def describe_secret_route() -> None:
    expected_request = {"account": "my-aws-account"}
    expected_secret = {"access_key": "AKIAIOSFODNN7EXAMPLE", "secret_key": "wJalrXUtnFEMI"}

    async def it_posts_a_payload_and_receives_the_expected_secret(
        mcp: FastMCP, http: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _handler(request: Request) -> Response:
            body = json.loads(await request.body())
            assert_that(body).is_equal_to(expected_request)
            return JSONResponse(expected_secret)

        monkeypatch.setattr(AwsSecretHandler, "handle", _handler)
        monkeypatch.setenv("TRUST_SERVERS", "aws=http://127.0.0.1:8080")
        await register(mcp, _http_client_factory=lambda _: http)
        result = await trust_client.get_trust_config().get_client("aws").post(expected_request)
        assert_that(result).is_equal_to(expected_secret)
