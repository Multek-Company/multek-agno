"""ContentModerationGuardrail — blocks inputs that match configurable blocked terms or regex patterns."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Union

from agno.exceptions import CheckTrigger, InputCheckError
from agno.guardrails.base import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput


class ContentModerationGuardrail(BaseGuardrail):
    """Blocks requests whose input matches any blocked term or regex pattern.

    Args:
        blocked_terms: Plain-text terms to block (case-insensitive substring match).
        blocked_patterns: Regex patterns to block (applied with ``re.IGNORECASE``).
        message: Custom error message when input is blocked.
    """

    def __init__(
        self,
        blocked_terms: Optional[Sequence[str]] = None,
        blocked_patterns: Optional[Sequence[str]] = None,
        message: str = "Input contains blocked content.",
    ) -> None:
        self.blocked_terms: List[str] = [t.lower() for t in (blocked_terms or [])]
        self.blocked_patterns: List[re.Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in (blocked_patterns or [])
        ]
        self.message = message

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Raise ``InputCheckError`` if the input matches any blocked term or pattern."""
        content = run_input.input_content_string().lower()

        for term in self.blocked_terms:
            if term in content:
                raise InputCheckError(
                    self.message,
                    check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
                )

        text = run_input.input_content_string()
        for pattern in self.blocked_patterns:
            if pattern.search(text):
                raise InputCheckError(
                    self.message,
                    check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
                )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Async variant — delegates to the synchronous check."""
        self.check(run_input)
