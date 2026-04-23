"""The `AskUserQuestionsToolkit` — lets an agent ask the user multiple-choice questions."""

from __future__ import annotations

import inspect
import json
from typing import List, Optional

from agno.tools.toolkit import Toolkit

from .prompt import DEFAULT_INSTRUCTIONS, MAX_QUESTIONS
from .renderers import QuestionRenderer
from .schemas import AskUserAnswer, AskUserQuestion


class AskUserQuestionsToolkit(Toolkit):
    """Lets the agent ask the user 1-5 multiple-choice questions in a single call.

    The toolkit has two modes:

    - **Inline mode (default, `external_execution=False`)**: a `QuestionRenderer`
      runs inside the agent process. Both a sync (`ask_user_questions`) and an
      async (`aask_user_questions`) entrypoint are registered under the same
      tool name, so `agent.run()` and `agent.arun()` both work. Sync renderers
      are offloaded to a worker thread from the async path so the event loop is
      never blocked. Sync agent + async renderer is rejected with `TypeError`.

    - **External-execution mode (`external_execution=True`)**: the agent pauses
      before calling the tool. Your frontend/client reads the paused run's
      `tool_args["questions"]`, renders its own UI, then resumes the run via
      `requirement.set_external_execution_result(json_string)` +
      `agent.continue_run(...)`. The returned JSON must be a list of
      `AskUserAnswer` objects (one per question, same order). No renderer is
      needed in this mode. See the Agno docs on human-in-the-loop external
      execution for the full pause/resume protocol.

    Args:
        renderer: Callable taking `List[AskUserQuestion]` and returning (or awaiting)
            `List[AskUserAnswer]`. Used only in inline mode. Defaults to
            `TerminalQuestionRenderer()` when `external_execution=False` and no
            renderer is provided. Ignored when `external_execution=True`.
        external_execution: When True, the tool pauses the agent so an external
            system (e.g. a web frontend) handles the UI and fills in the answer.
            Mutually exclusive with having a renderer — passing both raises
            `ValueError`.
        external_execution_silent: When True, suppresses Agno's verbose
            "Run is paused. The following tool calls require external execution..."
            console output. Useful when the pause is handled entirely by your
            frontend and you don't want stdout noise. Only meaningful alongside
            `external_execution=True`; passing it with inline mode raises
            `ValueError`.
        instructions: Override the default LLM instructions. When `None`, the
            built-in prompt is used.
        add_instructions: Forwarded to `Toolkit`. When `True` (default), the
            instructions are appended to the agent's system prompt.
    """

    def __init__(
        self,
        renderer: Optional[QuestionRenderer] = None,
        external_execution: bool = False,
        external_execution_silent: bool = False,
        instructions: Optional[str] = None,
        add_instructions: bool = True,
    ) -> None:
        if external_execution and renderer is not None:
            raise ValueError(
                "external_execution=True is incompatible with a renderer. "
                "In external-execution mode the agent pauses and your frontend fills "
                "in the answer; there is nothing for a renderer to render."
            )
        if external_execution_silent and not external_execution:
            raise ValueError(
                "external_execution_silent=True requires external_execution=True. "
                "The flag only affects the pause-output console formatting, which "
                "is only produced when the tool actually pauses."
            )

        self.external_execution: bool = external_execution
        self.external_execution_silent: bool = external_execution_silent
        self.renderer: Optional[QuestionRenderer]

        if external_execution:
            self.renderer = None
        else:
            if renderer is None:
                from .renderers.terminal import TerminalQuestionRenderer

                renderer = TerminalQuestionRenderer()
            self.renderer = renderer

        super().__init__(
            name="ask_user_questions",
            tools=[self.ask_user_questions],
            async_tools=[(self.aask_user_questions, "ask_user_questions")],
            instructions=instructions or DEFAULT_INSTRUCTIONS,
            add_instructions=add_instructions,
            show_result_tools=["ask_user_questions"],
            external_execution_required_tools=(["ask_user_questions"] if external_execution else []),
        )

        # `Toolkit` doesn't take an `external_execution_silent_tools` list, so we
        # set the flag on the underlying `Function` objects after registration.
        # Agno reads `fc.function.external_execution_silent` when building the
        # paused ToolExecution (see agno/models/base.py) and when deciding whether
        # to render the "Run is paused..." panel (see agno/utils/response.py).
        if external_execution_silent:
            for fn_dict in (self.functions, self.async_functions):
                fn = fn_dict.get("ask_user_questions")
                if fn is not None:
                    fn.external_execution_silent = True

    def ask_user_questions(self, questions: List[AskUserQuestion]) -> str:
        """Present 1-5 multiple-choice questions to the user and return their answers.

        Each question has 2-4 options plus an automatic "Other" free-text field (do
        not include "Other" as an option — it is provided by the UI). Use this tool
        to clarify ambiguity, gather preferences, or offer decision points.

        Args:
            questions: 1-5 questions. Each has:
                - `question`: clear question ending with a question mark
                - `hint` (optional): one-line subtitle clarifying the question
                - `options`: 2-4 items, each with `title` (1-5 words) and optional
                  `description`
                - `multi_select`: true to allow multiple selections (checkbox);
                  false for radio (default)

        Returns:
            JSON string — a list of `{question, user_answer, other_text, skipped}`.
            `user_answer` is a list of the option titles the user selected
            (0 or 1 for single-select, 0..n for multi-select). It is empty when
            the user skipped or only used the free-text "Other" field.
        """
        _validate(questions)
        self._reject_external_execution_call()
        assert self.renderer is not None  # guaranteed by _reject_external_execution_call
        result = self.renderer(questions)
        if inspect.isawaitable(result):
            raise TypeError(
                "An async QuestionRenderer cannot be used under agent.run(). "
                "Use agent.arun() (which calls aask_user_questions), or pass a sync renderer."
            )
        return json.dumps([a.model_dump() for a in result])

    async def aask_user_questions(self, questions: List[AskUserQuestion]) -> str:
        """Async variant of `ask_user_questions`, used automatically by `agent.arun()`.

        Sync renderers are offloaded to a worker thread so they do not block the
        event loop. Async renderers are awaited directly. See `ask_user_questions`
        for parameter/return details.
        """
        _validate(questions)
        self._reject_external_execution_call()
        answers = await self._invoke_renderer(questions)
        return json.dumps([a.model_dump() for a in answers])

    def _reject_external_execution_call(self) -> None:
        if self.external_execution:
            raise RuntimeError(
                "ask_user_questions should not execute when external_execution=True; "
                "Agno is expected to pause before calling this tool so your frontend "
                "can provide the answer via requirement.set_external_execution_result(). "
                "If you're seeing this error, the pause machinery is not wired up."
            )

    async def _invoke_renderer(self, questions: List[AskUserQuestion]) -> List[AskUserAnswer]:
        renderer = self.renderer
        assert renderer is not None  # guaranteed by _reject_external_execution_call
        if _is_async_callable(renderer):
            result = await renderer(questions)  # type: ignore[misc]
            return list(result)

        import anyio

        def _call_sync() -> List[AskUserAnswer]:
            return list(renderer(questions))  # type: ignore[arg-type]

        return await anyio.to_thread.run_sync(_call_sync)


def _validate(questions: List[AskUserQuestion]) -> None:
    if not questions:
        raise ValueError("At least one question is required.")
    if len(questions) > MAX_QUESTIONS:
        raise ValueError(f"Max {MAX_QUESTIONS} questions per call (got {len(questions)}).")


def _is_async_callable(obj: object) -> bool:
    """Detect whether calling `obj(...)` returns a coroutine, without calling it."""
    if inspect.iscoroutinefunction(obj):
        return True
    call = getattr(obj, "__call__", None)
    return inspect.iscoroutinefunction(call)
