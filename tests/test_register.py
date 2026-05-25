from ai_contained.trust.client import TrustConfig, get_trust_config, init_trust_config
from fastmcp import FastMCP

from ai_contained.provider.trust_client import register


def describe_register() -> None:
    def it_is_callable_with_a_fastmcp_instance(mcp: FastMCP) -> None:
        pass  # fixture itself verifies this

    def it_exposes_trust_client_imports() -> None:
        assert get_trust_config is not None
        assert init_trust_config is not None
        assert TrustConfig is not None
