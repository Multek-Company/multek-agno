"""Tests for rate-limit hook."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

from multek_agno.hooks.rate_limit import RateLimitExceeded, create_rate_limit_hook


def _make_fc(name: str = "my_tool") -> MagicMock:
    fc = MagicMock()
    fc.function.name = name
    return fc


# ---------------------------------------------------------------------------
# Basic rate limiting
# ---------------------------------------------------------------------------


def test_allows_calls_within_limit() -> None:
    hook = create_rate_limit_hook(max_calls=3, window_seconds=60)
    fc = _make_fc()
    for _ in range(3):
        hook(fc)  # should not raise


def test_blocks_call_over_limit() -> None:
    hook = create_rate_limit_hook(max_calls=2, window_seconds=60)
    fc = _make_fc()
    hook(fc)
    hook(fc)
    with pytest.raises(RateLimitExceeded):
        hook(fc)


# ---------------------------------------------------------------------------
# Window expiry
# ---------------------------------------------------------------------------


def test_allows_after_window_expires() -> None:
    hook = create_rate_limit_hook(max_calls=1, window_seconds=0.5)
    fc = _make_fc()
    hook(fc)
    with pytest.raises(RateLimitExceeded):
        hook(fc)
    time.sleep(0.6)
    hook(fc)  # should succeed after window expires


# ---------------------------------------------------------------------------
# Per-tool vs shared
# ---------------------------------------------------------------------------


def test_per_tool_separate_counters() -> None:
    hook = create_rate_limit_hook(max_calls=1, window_seconds=60, per_tool=True)
    hook(_make_fc("tool_a"))
    hook(_make_fc("tool_b"))  # different tool, should be fine


def test_shared_counter() -> None:
    hook = create_rate_limit_hook(max_calls=1, window_seconds=60, per_tool=False)
    hook(_make_fc("tool_a"))
    with pytest.raises(RateLimitExceeded):
        hook(_make_fc("tool_b"))  # shared counter, blocked


# ---------------------------------------------------------------------------
# Exception details
# ---------------------------------------------------------------------------


def test_exception_has_retry_after() -> None:
    hook = create_rate_limit_hook(max_calls=1, window_seconds=60)
    fc = _make_fc("search")
    hook(fc)
    with pytest.raises(RateLimitExceeded) as exc_info:
        hook(fc)
    assert exc_info.value.tool_name == "search"
    assert exc_info.value.retry_after > 0
