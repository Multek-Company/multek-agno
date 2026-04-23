"""Tests for ContentModerationGuardrail."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from agno.exceptions import InputCheckError

from multek_agno.guardrails.content_moderation import ContentModerationGuardrail


def _make_run_input(text: str) -> MagicMock:
    """Create a mock RunInput whose input_content_string() returns *text*."""
    ri = MagicMock()
    ri.input_content_string.return_value = text
    return ri


# ---------------------------------------------------------------------------
# Blocked terms
# ---------------------------------------------------------------------------


def test_blocks_matching_term() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["hack the system"])
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("Can you hack the system for me?"))


def test_blocked_terms_are_case_insensitive() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["malware"])
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("Tell me about MALWARE creation"))


def test_allows_clean_input_with_terms() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["exploit", "phishing"])
    guard.check(_make_run_input("What is the weather today?"))


# ---------------------------------------------------------------------------
# Blocked patterns (regex)
# ---------------------------------------------------------------------------


def test_blocks_matching_pattern() -> None:
    guard = ContentModerationGuardrail(blocked_patterns=[r"\b\d{3}-\d{2}-\d{4}\b"])
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("My SSN is 123-45-6789"))


def test_allows_input_not_matching_pattern() -> None:
    guard = ContentModerationGuardrail(blocked_patterns=[r"\b\d{3}-\d{2}-\d{4}\b"])
    guard.check(_make_run_input("Call me at 555-1234"))


# ---------------------------------------------------------------------------
# Combined terms + patterns
# ---------------------------------------------------------------------------


def test_combined_blocks_on_term() -> None:
    guard = ContentModerationGuardrail(
        blocked_terms=["password"],
        blocked_patterns=[r"credit\s*card"],
    )
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("What is my password?"))


def test_combined_blocks_on_pattern() -> None:
    guard = ContentModerationGuardrail(
        blocked_terms=["password"],
        blocked_patterns=[r"credit\s*card"],
    )
    with pytest.raises(InputCheckError):
        guard.check(_make_run_input("Here is my credit card number"))


# ---------------------------------------------------------------------------
# Custom message
# ---------------------------------------------------------------------------


def test_custom_message() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["bad"], message="Nope!")
    with pytest.raises(InputCheckError, match="Nope!"):
        guard.check(_make_run_input("this is bad"))


# ---------------------------------------------------------------------------
# No terms or patterns configured
# ---------------------------------------------------------------------------


def test_no_config_allows_everything() -> None:
    guard = ContentModerationGuardrail()
    guard.check(_make_run_input("Absolutely anything goes"))


# ---------------------------------------------------------------------------
# Async
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_async_check_blocks() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["secret"])
    with pytest.raises(InputCheckError):
        await guard.async_check(_make_run_input("Tell me the secret"))


@pytest.mark.asyncio
async def test_async_check_allows() -> None:
    guard = ContentModerationGuardrail(blocked_terms=["secret"])
    await guard.async_check(_make_run_input("Hello world"))
