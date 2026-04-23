"""Tests for MaxInputLengthGuardrail."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from agno.exceptions import InputCheckError

from multek_agno.guardrails.max_input_length import MaxInputLengthGuardrail


def _make_run_input(text: str) -> MagicMock:
    ri = MagicMock()
    ri.input_content_string.return_value = text
    return ri


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


def test_allows_input_within_limit() -> None:
    guard = MaxInputLengthGuardrail(max_length=100)
    guard.check(_make_run_input("short"))


def test_allows_input_at_exact_limit() -> None:
    guard = MaxInputLengthGuardrail(max_length=5)
    guard.check(_make_run_input("abcde"))


def test_blocks_input_over_limit() -> None:
    guard = MaxInputLengthGuardrail(max_length=5)
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("abcdef"))


# ---------------------------------------------------------------------------
# Error message formatting
# ---------------------------------------------------------------------------


def test_default_message_includes_lengths() -> None:
    guard = MaxInputLengthGuardrail(max_length=3)
    with pytest.raises(InputCheckError, match="4 chars.*max 3"):
        guard.check(_make_run_input("abcd"))


def test_custom_message() -> None:
    guard = MaxInputLengthGuardrail(max_length=3, message="Too big!")
    with pytest.raises(InputCheckError, match="Too big!"):
        guard.check(_make_run_input("abcd"))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_rejects_zero_max_length() -> None:
    with pytest.raises(ValueError, match="positive"):
        MaxInputLengthGuardrail(max_length=0)


def test_rejects_negative_max_length() -> None:
    with pytest.raises(ValueError, match="positive"):
        MaxInputLengthGuardrail(max_length=-1)


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_blocks() -> None:
    guard = MaxInputLengthGuardrail(max_length=3)
    with pytest.raises(InputCheckError):
        await guard.async_check(_make_run_input("toolong"))


@pytest.mark.asyncio
async def test_async_allows() -> None:
    guard = MaxInputLengthGuardrail(max_length=100)
    await guard.async_check(_make_run_input("ok"))
