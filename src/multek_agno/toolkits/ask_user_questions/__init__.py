"""Multiple-choice question toolkit for Agno agents.

Exports:
    - `AskUserQuestionsToolkit`: the toolkit to register with an agent
    - `AskUserQuestion`, `AskUserOption`, `AskUserAnswer`: Pydantic schemas
    - `QuestionRenderer`: Protocol consumers implement to render questions elsewhere
      (web, Telegram, etc.)
    - `TerminalQuestionRenderer`: reference renderer (requires the `[terminal]` extra)
"""

from .renderers import QuestionRenderer
from .schemas import AskUserAnswer, AskUserOption, AskUserQuestion
from .toolkit import AskUserQuestionsToolkit


def __getattr__(name: str) -> object:
    if name == "TerminalQuestionRenderer":
        from .renderers.terminal import TerminalQuestionRenderer

        return TerminalQuestionRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AskUserAnswer",
    "AskUserOption",
    "AskUserQuestion",
    "AskUserQuestionsToolkit",
    "QuestionRenderer",
    "TerminalQuestionRenderer",
]
