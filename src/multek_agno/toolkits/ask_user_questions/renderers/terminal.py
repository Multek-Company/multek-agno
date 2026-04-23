"""Reference interactive terminal renderer built on `prompt_toolkit`.

Shows one question at a time, matching the layout described in the plan file
(question + optional hint, numbered options, "Outro..." free-text field, Pular
skip button, keyboard hints). Supports single-select (radio) and multi-select
(checkbox) via `AskUserQuestion.multi_select`.

This renderer requires the `terminal` extra. Install with:

    pip install multek-agno[terminal]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Set

from ..schemas import AskUserAnswer, AskUserQuestion


def _import_prompt_toolkit() -> None:
    try:
        import prompt_toolkit  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "TerminalQuestionRenderer requires the 'terminal' extra. Install with: pip install multek-agno[terminal]"
        ) from exc


@dataclass
class _QuestionState:
    cursor: int = 0  # highlighted option index
    checked: Set[int] = field(default_factory=set)  # for multi-select
    result: Optional[AskUserAnswer] = None


class TerminalQuestionRenderer:
    """Interactive terminal renderer for `AskUserQuestion` using prompt_toolkit."""

    def __call__(self, questions: List[AskUserQuestion]) -> List[AskUserAnswer]:
        _import_prompt_toolkit()
        total = len(questions)
        answers: List[AskUserAnswer] = []
        for idx, question in enumerate(questions):
            answers.append(_run_single_question(question, index=idx, total=total))
        return answers


def _run_single_question(question: AskUserQuestion, *, index: int, total: int) -> AskUserAnswer:
    from prompt_toolkit import Application
    from prompt_toolkit.buffer import Buffer
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.layout import HSplit, Layout, VSplit, Window, WindowAlign
    from prompt_toolkit.layout.containers import ConditionalContainer
    from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
    from prompt_toolkit.styles import Style

    state = _QuestionState()
    outro_buffer = Buffer(multiline=False)

    # --- Controls -----------------------------------------------------------
    options_control = FormattedTextControl(
        lambda: _render_options(question, state),
        focusable=True,
        show_cursor=False,
    )
    outro_control = BufferControl(buffer=outro_buffer, focusable=True)

    header_left = FormattedTextControl(lambda: [("class:question", question.question)])
    header_right = FormattedTextControl(
        lambda: [
            ("class:counter", f"{index + 1} de {total}"),
            ("", "   "),
            ("class:close", "✕"),
        ]
    )
    hint_control = FormattedTextControl(lambda: [("class:hint", question.hint or "")])
    footer_control = FormattedTextControl(lambda: _render_footer(question.multi_select, _is_outro_focused()))
    skip_control = FormattedTextControl(lambda: [("class:skip", "[ Pular ]")])
    outro_prefix = FormattedTextControl(lambda: [("class:outro-icon", "✎ ")])

    # --- Layout -------------------------------------------------------------
    def divider() -> Window:
        return Window(
            FormattedTextControl(lambda: [("class:border", "─" * 80)]),
            height=1,
        )

    header_row = VSplit(
        [
            Window(header_left),
            Window(header_right, align=WindowAlign.RIGHT, dont_extend_width=True),
        ]
    )

    hint_row = ConditionalContainer(
        Window(hint_control, height=1),
        filter=Condition(lambda: bool(question.hint)),
    )

    options_window = Window(options_control, dont_extend_height=True, wrap_lines=True)

    outro_row = VSplit(
        [
            Window(outro_prefix, width=2, dont_extend_width=True),
            Window(outro_control, height=1),
            Window(skip_control, width=11, align=WindowAlign.RIGHT, dont_extend_width=True),
        ],
        height=1,
    )

    footer_row = Window(footer_control, height=1)

    body = HSplit(
        [
            header_row,
            hint_row,
            divider(),
            options_window,
            divider(),
            outro_row,
            divider(),
            footer_row,
        ]
    )

    layout = Layout(body)

    def _is_outro_focused() -> bool:
        return layout.has_focus(outro_control)

    # --- Key bindings -------------------------------------------------------
    kb = KeyBindings()

    def _submit_from_options() -> Optional[AskUserAnswer]:
        if question.multi_select:
            selected = [question.options[i].title for i in sorted(state.checked)]
            outro_text = outro_buffer.text.strip() or None
            if not selected and not outro_text:
                return None  # block empty submit
            return AskUserAnswer(
                question=question.question,
                user_answer=selected,
                other_text=outro_text,
                skipped=False,
            )
        return AskUserAnswer(
            question=question.question,
            user_answer=[question.options[state.cursor].title],
            other_text=None,
            skipped=False,
        )

    def _submit_from_outro() -> Optional[AskUserAnswer]:
        outro_text = outro_buffer.text.strip() or None
        if question.multi_select:
            selected = [question.options[i].title for i in sorted(state.checked)]
            if not selected and not outro_text:
                return None
            return AskUserAnswer(
                question=question.question,
                user_answer=selected,
                other_text=outro_text,
                skipped=False,
            )
        if not outro_text:
            return None
        return AskUserAnswer(
            question=question.question,
            user_answer=[],
            other_text=outro_text,
            skipped=False,
        )

    @kb.add("c-c", eager=True)
    def _(event: Any) -> None:
        event.app.exit(exception=KeyboardInterrupt())

    @kb.add("escape", eager=True)
    def _(event: Any) -> None:
        state.result = AskUserAnswer(
            question=question.question,
            user_answer=[],
            other_text=None,
            skipped=True,
        )
        event.app.exit()

    @kb.add("tab")
    def _(event: Any) -> None:
        if _is_outro_focused():
            event.app.layout.focus(options_control)
        else:
            event.app.layout.focus(outro_control)

    @kb.add("s-tab")
    def _(event: Any) -> None:
        if _is_outro_focused():
            event.app.layout.focus(options_control)
        else:
            event.app.layout.focus(outro_control)

    @kb.add("up")
    def _(event: Any) -> None:
        if _is_outro_focused():
            # Return to the last option.
            state.cursor = len(question.options) - 1
            event.app.layout.focus(options_control)
        elif state.cursor > 0:
            state.cursor -= 1

    @kb.add("down")
    def _(event: Any) -> None:
        if _is_outro_focused():
            return  # already at the bottom
        if state.cursor < len(question.options) - 1:
            state.cursor += 1
        else:
            # Past the last option → focus the Outro free-text input.
            event.app.layout.focus(outro_control)

    @kb.add("space", filter=Condition(lambda: question.multi_select and not _is_outro_focused()))
    def _(event: Any) -> None:
        if state.cursor in state.checked:
            state.checked.remove(state.cursor)
        else:
            state.checked.add(state.cursor)

    for i in range(len(question.options)):
        key = str(i + 1)

        @kb.add(key, filter=Condition(lambda: not _is_outro_focused()))
        def _(event: Any, idx: int = i) -> None:  # idx captured via default arg
            state.cursor = idx
            if question.multi_select:
                if idx in state.checked:
                    state.checked.remove(idx)
                else:
                    state.checked.add(idx)

    @kb.add("enter")
    def _(event: Any) -> None:
        answer = _submit_from_outro() if _is_outro_focused() else _submit_from_options()
        if answer is not None:
            state.result = answer
            event.app.exit()

    # --- Styles -------------------------------------------------------------
    style = Style.from_dict(
        {
            "question": "bold",
            "counter": "#888888",
            "close": "#888888",
            "hint": "#6b7280 italic",
            "border": "#d4d4d4",
            "badge-selected": "bg:#d97706 #ffffff bold",
            "badge-unselected": "bg:#e5e7eb #6b7280",
            "badge-checked": "bg:#d97706 #ffffff bold",
            "title-selected": "bold",
            "title-unselected": "",
            "desc": "#9ca3af italic",
            "cursor": "#d97706 bold",
            "chevron": "#d97706",
            "outro-icon": "#9ca3af",
            "skip": "#374151",
            "footer": "#9ca3af",
        }
    )

    app: Application[None] = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        full_screen=False,
        mouse_support=False,
    )
    layout.focus(options_control)
    app.run()

    if state.result is None:
        return AskUserAnswer(
            question=question.question,
            user_answer=[],
            other_text=None,
            skipped=True,
        )
    return state.result


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _render_options(question: AskUserQuestion, state: _QuestionState) -> list[tuple[str, str]]:
    """Build the formatted-text list for the options area."""
    fragments: list[tuple[str, str]] = []
    for i, option in enumerate(question.options):
        is_cursor = i == state.cursor
        is_checked = i in state.checked

        if question.multi_select:
            badge_mark = "✓" if is_checked else " "
            badge_style = "class:badge-checked" if is_checked else "class:badge-unselected"
            badge = f" [{badge_mark}] "
        else:
            badge_style = "class:badge-selected" if (is_cursor) else "class:badge-unselected"
            badge = f" {i + 1} "

        cursor_glyph = "❯ " if is_cursor else "  "
        title_style = "class:title-selected" if is_cursor else "class:title-unselected"

        fragments.append(("class:cursor", cursor_glyph))
        fragments.append((badge_style, badge))
        fragments.append(("", "  "))
        fragments.append((title_style, option.title))
        if is_cursor and not question.multi_select:
            fragments.append(("class:chevron", "   ›"))
        fragments.append(("", "\n"))
        if option.description:
            fragments.append(("", "        "))  # indent
            fragments.append(("class:desc", option.description))
            fragments.append(("", "\n"))
    if fragments and fragments[-1] == ("", "\n"):
        fragments.pop()  # trim trailing newline
    return fragments


def _render_footer(multi_select: bool, outro_focused: bool) -> list[tuple[str, str]]:
    if outro_focused:
        parts = [
            "Digite sua resposta",
            "Enter para enviar",
            "Tab para voltar às opções",
            "Esc para pular",
        ]
    elif multi_select:
        parts = [
            "Setas para navegar",
            "Espaço para marcar",
            "Enter para enviar",
            "Esc para pular",
        ]
    else:
        parts = [
            "Setas para navegar",
            "Enter para selecionar",
            "Esc para pular",
        ]
    joined = "  ·  ".join(parts)
    return [("class:footer", f"   {joined}   ")]
