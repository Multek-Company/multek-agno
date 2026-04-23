"""Renderer protocol + lazy accessors for built-in renderers.

A renderer is any callable that takes a list of `AskUserQuestion` objects and
returns (or awaits and returns) a list of `AskUserAnswer` objects, one per
input question, in the same order.

Sync renderers are offloaded to a worker thread by the toolkit so they do not
block the event loop when the agent is driven by `agent.arun()`.
"""

from __future__ import annotations

from typing import Awaitable, List, Protocol, Union, runtime_checkable

from ..schemas import AskUserAnswer, AskUserQuestion


@runtime_checkable
class QuestionRenderer(Protocol):
    """Shows questions to the user and returns their answers.

    May be sync or async. Must return exactly one `AskUserAnswer` per input question,
    in the same order.
    """

    def __call__(
        self, questions: List[AskUserQuestion]
    ) -> Union[List[AskUserAnswer], Awaitable[List[AskUserAnswer]]]: ...


def __getattr__(name: str) -> object:
    # Lazy-import the reference terminal renderer so consumers that don't install
    # the `terminal` extra don't pay the import cost (or see an ImportError) unless
    # they actually reach for it.
    if name == "TerminalQuestionRenderer":
        from .terminal import TerminalQuestionRenderer

        return TerminalQuestionRenderer
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["QuestionRenderer", "TerminalQuestionRenderer"]
