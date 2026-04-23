"""Pydantic schemas for the ask_user_questions toolkit."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class AskUserOption(BaseModel):
    """A single choice the user can select."""

    title: str = Field(
        ...,
        description="Short display text for this option (1-5 words).",
    )
    description: Optional[str] = Field(
        None,
        description=(
            "Optional clarifier shown below the title when the user needs more context to choose between options."
        ),
    )


class AskUserQuestion(BaseModel):
    """A single question with 2-4 predefined options."""

    question: str = Field(
        ...,
        description="The question to ask the user. Should end with a question mark.",
    )
    hint: Optional[str] = Field(
        None,
        description=(
            "Optional one-line subtitle clarifying the question. Hidden when null. "
            "Use only when the question alone is ambiguous."
        ),
    )
    options: List[AskUserOption] = Field(
        ...,
        min_length=2,
        max_length=4,
        description="2-4 options. 'Other' is added automatically by the UI — do not include it here.",
    )
    multi_select: bool = Field(
        False,
        description=("If true, the user may pick more than one option (checkbox). Default false (radio)."),
    )


class AskUserAnswer(BaseModel):
    """The user's answer to a single question."""

    question: str = Field(..., description="The original question text, echoed back for correlation.")
    user_answer: List[str] = Field(
        default_factory=list,
        description=(
            "The option title(s) the user selected, in the order shown to them. Empty list "
            "if the user only typed free-text in `other_text` or if they skipped the question. "
            "For single-select this has 0 or 1 elements; for multi-select it can have any number."
        ),
    )
    other_text: Optional[str] = Field(
        None,
        description="Free-text the user typed into the 'Outro...' field, if any. Null otherwise.",
    )
    skipped: bool = Field(
        False,
        description=(
            "True if the user pressed Esc / chose 'Pular' without answering. "
            "Both user_answer and other_text will be empty/null when this is True."
        ),
    )
