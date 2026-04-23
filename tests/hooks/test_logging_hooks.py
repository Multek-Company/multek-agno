"""Tests for logging hooks."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

from multek_agno.hooks.logging_hooks import create_logging_hooks


def _make_fc(name: str = "my_tool", arguments: dict | None = None, result: object = None) -> MagicMock:
    """Create a mock FunctionCall."""
    fc = MagicMock()
    fc.function.name = name
    fc.arguments = arguments or {}
    fc.result = result
    return fc


# ---------------------------------------------------------------------------
# Basic logging
# ---------------------------------------------------------------------------


def test_pre_hook_logs_tool_name(caplog: logging.LogRecord) -> None:  # type: ignore[type-arg]
    pre, _ = create_logging_hooks()
    fc = _make_fc("search", {"query": "test"})
    with caplog.at_level(logging.INFO, logger="multek_agno.hooks"):
        pre(fc)
    assert "search" in caplog.text


def test_post_hook_logs_elapsed(caplog: logging.LogRecord) -> None:  # type: ignore[type-arg]
    pre, post = create_logging_hooks()
    fc = _make_fc("search")
    with caplog.at_level(logging.INFO, logger="multek_agno.hooks"):
        pre(fc)
        post(fc)
    assert "elapsed=" in caplog.text


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------


def test_log_arguments_false_hides_args(caplog: logging.LogRecord) -> None:  # type: ignore[type-arg]
    pre, _ = create_logging_hooks(log_arguments=False)
    fc = _make_fc("search", {"query": "secret"})
    with caplog.at_level(logging.INFO, logger="multek_agno.hooks"):
        pre(fc)
    assert "secret" not in caplog.text


def test_log_result_true_shows_result(caplog: logging.LogRecord) -> None:  # type: ignore[type-arg]
    pre, post = create_logging_hooks(log_result=True)
    fc = _make_fc("search", result="found it")
    with caplog.at_level(logging.INFO, logger="multek_agno.hooks"):
        pre(fc)
        post(fc)
    assert "found it" in caplog.text


def test_long_result_is_truncated(caplog: logging.LogRecord) -> None:  # type: ignore[type-arg]
    pre, post = create_logging_hooks(log_result=True)
    fc = _make_fc("search", result="x" * 300)
    with caplog.at_level(logging.INFO, logger="multek_agno.hooks"):
        pre(fc)
        post(fc)
    assert "..." in caplog.text


# ---------------------------------------------------------------------------
# Custom logger
# ---------------------------------------------------------------------------


def test_custom_logger() -> None:
    custom = logging.getLogger("custom_test")
    custom.setLevel(logging.DEBUG)
    handler = logging.handlers.MemoryHandler(capacity=100) if hasattr(logging, "handlers") else logging.StreamHandler()

    pre, post = create_logging_hooks(custom_logger=custom)
    fc = _make_fc("tool")
    # Should not raise
    pre(fc)
    post(fc)
