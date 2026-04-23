"""Tests for AskUserQuestionsToolkit."""

from __future__ import annotations

import asyncio
import json
from typing import List

import pytest
from pydantic import ValidationError

from multek_agno.toolkits.ask_user_questions import (
    AskUserAnswer,
    AskUserOption,
    AskUserQuestion,
    AskUserQuestionsToolkit,
)
from multek_agno.toolkits.ask_user_questions.prompt import MAX_OPTIONS, MAX_QUESTIONS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _simple_question(
    text: str = "Which one?",
    n_opts: int = 2,
    multi: bool = False,
    hint: str | None = None,
) -> AskUserQuestion:
    return AskUserQuestion(
        question=text,
        hint=hint,
        options=[AskUserOption(title=f"Option {i}") for i in range(1, n_opts + 1)],
        multi_select=multi,
    )


class _CannedRenderer:
    """Deterministic renderer that returns pre-baked answers."""

    def __init__(self, answers: List[AskUserAnswer]) -> None:
        self.answers = answers
        self.received: list[List[AskUserQuestion]] = []

    def __call__(self, questions: List[AskUserQuestion]) -> List[AskUserAnswer]:
        self.received.append(questions)
        return self.answers


class _AsyncCannedRenderer:
    def __init__(self, answers: List[AskUserAnswer]) -> None:
        self.answers = answers

    async def __call__(self, questions: List[AskUserQuestion]) -> List[AskUserAnswer]:
        return self.answers


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_option_requires_title() -> None:
    with pytest.raises(ValidationError):
        AskUserOption()  # type: ignore[call-arg]


def test_option_description_optional() -> None:
    opt = AskUserOption(title="Hi")
    assert opt.description is None


def test_question_min_two_options() -> None:
    with pytest.raises(ValidationError):
        AskUserQuestion(
            question="Q?",
            options=[AskUserOption(title="only one")],
        )


def test_question_max_four_options() -> None:
    with pytest.raises(ValidationError):
        AskUserQuestion(
            question="Q?",
            options=[AskUserOption(title=f"opt{i}") for i in range(MAX_OPTIONS + 1)],
        )


def test_question_hint_defaults_to_none() -> None:
    q = _simple_question()
    assert q.hint is None


def test_question_multi_select_defaults_false() -> None:
    q = _simple_question()
    assert q.multi_select is False


def test_answer_defaults() -> None:
    a = AskUserAnswer(question="Q?")
    assert a.user_answer == []
    assert a.other_text is None
    assert a.skipped is False


# ---------------------------------------------------------------------------
# Toolkit registration
# ---------------------------------------------------------------------------


def test_toolkit_registers_both_sync_and_async_variants() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    # Sync path (agent.run) — registered via `tools=`
    assert "ask_user_questions" in toolkit.functions
    # Async path (agent.arun) — registered via `async_tools=`
    assert "ask_user_questions" in toolkit.async_functions
    # Merged view under async mode uses the async variant.
    assert "ask_user_questions" in toolkit.get_async_functions()


def test_toolkit_show_result_flag() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    assert toolkit.functions["ask_user_questions"].show_result is True
    assert toolkit.async_functions["ask_user_questions"].show_result is True


def test_toolkit_has_default_instructions() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    assert toolkit.instructions is not None
    assert "ask_user_questions" in toolkit.instructions
    assert str(MAX_QUESTIONS) in toolkit.instructions
    assert str(MAX_OPTIONS) in toolkit.instructions


def test_toolkit_custom_instructions() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]), instructions="Custom instructions.")
    assert toolkit.instructions == "Custom instructions."


# ---------------------------------------------------------------------------
# ask_user_questions (sync) — happy path
# ---------------------------------------------------------------------------


def test_ask_user_questions_sync_round_trip_single_select() -> None:
    question = _simple_question("Pick one?", n_opts=3)
    renderer = _CannedRenderer([AskUserAnswer(question="Pick one?", user_answer=["Option 2"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result_str = toolkit.ask_user_questions(questions=[question])
    result = json.loads(result_str)

    assert result == [
        {
            "question": "Pick one?",
            "user_answer": ["Option 2"],
            "other_text": None,
            "skipped": False,
        }
    ]
    # The renderer saw exactly the input question, exactly once.
    assert renderer.received == [[question]]


def test_ask_user_questions_sync_multi_select() -> None:
    question = _simple_question("Pick many?", n_opts=3, multi=True)
    renderer = _CannedRenderer([AskUserAnswer(question="Pick many?", user_answer=["Option 1", "Option 3"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(toolkit.ask_user_questions(questions=[question]))
    assert result[0]["user_answer"] == ["Option 1", "Option 3"]


def test_ask_user_questions_sync_skip_branch() -> None:
    question = _simple_question()
    renderer = _CannedRenderer([AskUserAnswer(question="Which one?", skipped=True)])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(toolkit.ask_user_questions(questions=[question]))
    assert result[0]["skipped"] is True
    assert result[0]["user_answer"] == []


def test_ask_user_questions_sync_other_text_branch() -> None:
    question = _simple_question()
    renderer = _CannedRenderer([AskUserAnswer(question="Which one?", other_text="My own answer")])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(toolkit.ask_user_questions(questions=[question]))
    assert result[0]["other_text"] == "My own answer"
    assert result[0]["user_answer"] == []


def test_ask_user_questions_sync_batch_of_multiple() -> None:
    questions = [_simple_question(f"Q{i}?") for i in range(3)]
    renderer = _CannedRenderer([AskUserAnswer(question=f"Q{i}?", user_answer=["Option 1"]) for i in range(3)])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(toolkit.ask_user_questions(questions=questions))
    assert [r["question"] for r in result] == ["Q0?", "Q1?", "Q2?"]


def test_ask_user_questions_sync_with_async_renderer_raises() -> None:
    """Sync agent.run() + async renderer is an invalid combination."""
    renderer = _AsyncCannedRenderer([AskUserAnswer(question="Q?", user_answer=["Option 1"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)
    with pytest.raises(TypeError, match="async QuestionRenderer"):
        toolkit.ask_user_questions(questions=[_simple_question("Q?")])


# ---------------------------------------------------------------------------
# aask_user_questions (async) — happy path
# ---------------------------------------------------------------------------


def test_aask_user_questions_with_async_renderer() -> None:
    question = _simple_question()
    renderer = _AsyncCannedRenderer([AskUserAnswer(question="Which one?", user_answer=["Option 1"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(asyncio.run(toolkit.aask_user_questions(questions=[question])))
    assert result[0]["user_answer"] == ["Option 1"]


def test_aask_user_questions_with_sync_renderer_calls_once() -> None:
    question = _simple_question()
    renderer = _CannedRenderer([AskUserAnswer(question="Which one?", user_answer=["Option 1"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    result = json.loads(asyncio.run(toolkit.aask_user_questions(questions=[question])))
    assert result[0]["user_answer"] == ["Option 1"]
    assert renderer.received == [[question]]  # called exactly once, not twice


# ---------------------------------------------------------------------------
# Error cases (validation runs on both variants)
# ---------------------------------------------------------------------------


def test_ask_user_questions_sync_empty_list_raises() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    with pytest.raises(ValueError, match="At least one question"):
        toolkit.ask_user_questions(questions=[])


def test_aask_user_questions_empty_list_raises() -> None:
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    with pytest.raises(ValueError, match="At least one question"):
        asyncio.run(toolkit.aask_user_questions(questions=[]))


def test_ask_user_questions_sync_too_many_raises() -> None:
    questions = [_simple_question(f"Q{i}?") for i in range(MAX_QUESTIONS + 1)]
    toolkit = AskUserQuestionsToolkit(renderer=_CannedRenderer([]))
    with pytest.raises(ValueError, match=f"Max {MAX_QUESTIONS} questions"):
        toolkit.ask_user_questions(questions=questions)


def test_ask_user_questions_sync_max_questions_allowed() -> None:
    questions = [_simple_question(f"Q{i}?") for i in range(MAX_QUESTIONS)]
    renderer = _CannedRenderer([AskUserAnswer(question=q.question, skipped=True) for q in questions])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)
    # Should not raise.
    toolkit.ask_user_questions(questions=questions)


# ---------------------------------------------------------------------------
# external_execution mode
# ---------------------------------------------------------------------------


def test_external_execution_registers_tool_for_pause() -> None:
    toolkit = AskUserQuestionsToolkit(external_execution=True)
    # Must still be registered under both sync and async paths so the tool is
    # visible to agent.run() and agent.arun(); Agno pauses before the body runs.
    assert "ask_user_questions" in toolkit.functions
    assert "ask_user_questions" in toolkit.async_functions
    # The relevant pause flag must be set on the Function.
    assert toolkit.functions["ask_user_questions"].external_execution is True
    assert toolkit.async_functions["ask_user_questions"].external_execution is True


def test_external_execution_has_no_renderer() -> None:
    toolkit = AskUserQuestionsToolkit(external_execution=True)
    assert toolkit.renderer is None


def test_external_execution_conflicts_with_renderer() -> None:
    with pytest.raises(ValueError, match="incompatible with a renderer"):
        AskUserQuestionsToolkit(
            external_execution=True,
            renderer=_CannedRenderer([]),
        )


def test_external_execution_body_raises_if_reached() -> None:
    """If Agno's pause machinery fails, direct call should fail loudly rather than crash on None."""
    toolkit = AskUserQuestionsToolkit(external_execution=True)
    with pytest.raises(RuntimeError, match="pause machinery"):
        toolkit.ask_user_questions(questions=[_simple_question()])


def test_external_execution_async_body_raises_if_reached() -> None:
    toolkit = AskUserQuestionsToolkit(external_execution=True)
    with pytest.raises(RuntimeError, match="pause machinery"):
        asyncio.run(toolkit.aask_user_questions(questions=[_simple_question()]))


def test_external_execution_silent_sets_flag_on_functions() -> None:
    toolkit = AskUserQuestionsToolkit(external_execution=True, external_execution_silent=True)
    assert toolkit.external_execution_silent is True
    # Flag propagates to both Function objects so Agno reads it at pause time.
    assert toolkit.functions["ask_user_questions"].external_execution_silent is True
    assert toolkit.async_functions["ask_user_questions"].external_execution_silent is True


def test_external_execution_silent_default_off() -> None:
    toolkit = AskUserQuestionsToolkit(external_execution=True)
    assert toolkit.external_execution_silent is False
    assert toolkit.functions["ask_user_questions"].external_execution_silent is not True
    assert toolkit.async_functions["ask_user_questions"].external_execution_silent is not True


def test_external_execution_silent_requires_external_execution() -> None:
    with pytest.raises(ValueError, match="requires external_execution=True"):
        AskUserQuestionsToolkit(external_execution_silent=True)


# ---------------------------------------------------------------------------
# Event-loop safety: sync renderer under arun must not block the loop
# ---------------------------------------------------------------------------


def test_aask_user_questions_offloads_sync_renderer_under_asyncio() -> None:
    """Sync renderer must be awaitable without blocking the event loop."""
    question = _simple_question()
    renderer = _CannedRenderer([AskUserAnswer(question="Which one?", user_answer=["Option 1"])])
    toolkit = AskUserQuestionsToolkit(renderer=renderer)

    async def _drive() -> str:
        # Run the async tool concurrently with another awaitable to sanity-check
        # that the event loop is not blocked by the sync renderer.
        tool_task = toolkit.aask_user_questions(questions=[question])
        other_task = asyncio.sleep(0)
        result, _ = await asyncio.gather(tool_task, other_task)
        return result

    result_str = asyncio.run(_drive())
    result = json.loads(result_str)
    assert result[0]["user_answer"] == ["Option 1"]
