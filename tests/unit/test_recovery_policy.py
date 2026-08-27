from __future__ import annotations

from app.modules.proxy.helpers import account_exhaustion_code_for_failover


def test_capacity_rate_limit_is_not_account_exhaustion() -> None:
    assert (
        account_exhaustion_code_for_failover(
            "rate_limit_exceeded",
            "Selected model is at capacity. Please try a different model.",
        )
        is None
    )


def test_usage_limit_rate_limit_is_account_exhaustion() -> None:
    assert (
        account_exhaustion_code_for_failover(
            "rate_limit_exceeded",
            "The usage limit has been reached",
        )
        == "rate_limit_exceeded"
    )


def test_message_only_usage_limit_is_account_exhaustion() -> None:
    assert (
        account_exhaustion_code_for_failover(
            "invalid_request_error",
            "The usage limit has been reached",
        )
        == "usage_limit_reached"
    )
