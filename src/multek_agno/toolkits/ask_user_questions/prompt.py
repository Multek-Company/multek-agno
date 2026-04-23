"""Instructions and constants injected into the agent's system prompt."""

from __future__ import annotations

from textwrap import dedent

MAX_QUESTIONS = 5
MAX_OPTIONS = 4  # per question; an automatic "Other" free-text field is added by the UI.

DEFAULT_INSTRUCTIONS = dedent(
    f"""\
    You have access to the `ask_user_questions` tool, which presents multiple-choice questions
    to the user and returns their selections.

    ## When to use it
    - Clarify ambiguous instructions before acting on them.
    - Gather user preferences or requirements you cannot infer.
    - Offer a concrete set of choices when there is real optionality in how to proceed.

    ## Hard limits
    - At most {MAX_QUESTIONS} questions per call.
    - Each question has 2-{MAX_OPTIONS} options.
    - DO NOT add an "Other" option — the UI provides a free-text "Outro..." field automatically.

    ## Field guidance
    - `question`: clear, specific, ends with a question mark.
    - `hint`: optional one-line subtitle. Include only when the question alone is ambiguous; otherwise omit it.
    - `options[].title`: 1-5 words. Distinct and mutually exclusive unless `multi_select` is true.
    - `options[].description`: optional. Include only when the title alone doesn't tell the user
      what picking it means (trade-offs, implications).
    - `multi_select`: set to true only when choices are not mutually exclusive; re-phrase accordingly
      ("Which features do you want?" not "Which option?").

    ## Recommendations
    - If you have a preferred option, make it the first one and append " (Recommended)" to its title.
    - Batch related questions into a single call rather than asking one at a time across turns.
    - The user may skip any question. If they do, proceed with best-effort assumptions and say so
      briefly in your next response — do not re-ask.

    ## Response shape
    The tool returns a JSON string: a list of `{{question, user_answer, other_text, skipped}}` objects.
    - `user_answer`: list of option titles the user picked (empty when they skipped or only used Outro).
    - `other_text`: the user's free-text entry when they used "Outro...", otherwise null.
    - `skipped`: true when the user chose "Pular" — treat this as "user declined to answer"
      and proceed with best-effort assumptions.
    """
)
