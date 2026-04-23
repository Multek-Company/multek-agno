"""MaxInputLengthGuardrail — rejects inputs that exceed a configurable character limit."""

from __future__ import annotations

from typing import Union

from agno.exceptions import CheckTrigger, InputCheckError
from agno.guardrails.base import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput


class MaxInputLengthGuardrail(BaseGuardrail):
    """Blocks requests whose input exceeds a maximum character length.

    Args:
        max_length: Maximum allowed number of characters.
        message: Custom error message. May contain ``{length}`` and ``{max_length}`` placeholders.
    """

    def __init__(
        self,
        max_length: int = 5000,
        message: str = "Input too long ({length} chars, max {max_length}).",
    ) -> None:
        if max_length <= 0:
            raise ValueError("max_length must be a positive integer")
        self.max_length = max_length
        self.message = message

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Raise ``InputCheckError`` if the input exceeds the character limit."""
        content = run_input.input_content_string()
        length = len(content)

        if length > self.max_length:
            raise InputCheckError(
                self.message.format(length=length, max_length=self.max_length),
                check_trigger=CheckTrigger.INPUT_NOT_ALLOWED,
            )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Async variant — delegates to the synchronous check."""
        self.check(run_input)
