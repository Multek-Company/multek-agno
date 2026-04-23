"""Manual smoke test for AskUserQuestionsToolkit's reference terminal renderer.

Run:

    uv run python examples/ask_user_questions_demo.py

What to verify when interacting with the TUI:
- `hint` hides itself entirely when it's None (question 1 below has no hint).
- Numbered badge (1..4) in an orange circle is highlighted on the focused option.
- Options with a `description` show a dim second line indented under the title.
- Arrow keys move the cursor; keys 1-4 jump directly to that option.
- Multi-select (question 2) uses checkboxes; Space toggles, Enter submits.
- Tab focuses the "Outro..." free-text field; typing works; Enter submits the
  free-text as `other_text`.
- Esc on any question records `skipped=True` and moves on.
- Ctrl+C aborts the whole run (KeyboardInterrupt).
- Final JSON echoes one answer object per question in order.
"""

from __future__ import annotations

import json

from multek_agno.toolkits.ask_user_questions import (
    AskUserOption,
    AskUserQuestion,
    AskUserQuestionsToolkit,
)


def main() -> None:
    questions = [
        AskUserQuestion(
            question="Qual tipo de material você precisa?",
            # hint omitted on purpose — verify the hint row disappears entirely.
            options=[
                AskUserOption(title="Cimento, areia e agregados"),
                AskUserOption(title="Tubos e conexões hidráulicas"),
                AskUserOption(title="Revestimentos e pisos"),
                AskUserOption(title="Material elétrico"),
            ],
        ),
        AskUserQuestion(
            question="Quais acabamentos você quer incluir?",
            hint="Você pode marcar mais de um — use Espaço para alternar.",
            multi_select=True,
            options=[
                AskUserOption(
                    title="Pintura",
                    description="Tinta, primer e complementos para parede interna/externa.",
                ),
                AskUserOption(
                    title="Rodapés",
                    description="MDF, madeira ou cerâmica.",
                ),
                AskUserOption(title="Forro de gesso"),
                AskUserOption(title="Porcelanato"),
            ],
        ),
        AskUserQuestion(
            question="Quem vai executar a obra?",
            hint="Essa informação ajuda a dimensionar a quantidade de material.",
            options=[
                AskUserOption(
                    title="Pedreiro próprio (Recomendado)",
                    description="Você já tem um pedreiro de confiança.",
                ),
                AskUserOption(
                    title="Empreiteira",
                    description="Contratação de uma empresa para executar a obra completa.",
                ),
                AskUserOption(
                    title="Ainda estou decidindo",
                    description="Não tenho certeza — preciso de mais orientação.",
                ),
            ],
        ),
    ]

    toolkit = AskUserQuestionsToolkit()
    result_json = toolkit.ask_user_questions(questions=questions)

    print()
    print("=== Resultado ===")
    print(json.dumps(json.loads(result_json), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
