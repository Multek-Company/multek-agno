# multek-agno

Reusable toolkits, guardrails, hooks, and skills for the [Agno Agents SDK](https://docs.agno.com).

## Installation

```bash
pip install multek-agno

# Optional: the reference terminal renderer for AskUserQuestionsToolkit
pip install multek-agno[terminal]
```

## What's Included

### Toolkits

- **`VisualizerToolkit`** — Lets agents generate interactive HTML/CSS/JS widgets inline, with optional file output and CDN library support. Also supports a frontend handoff mode via Agno's `external_execution` pause/resume.
- **`AskUserQuestionsToolkit`** — Lets agents ask the user up to 5 multiple-choice questions (radio or checkbox) in a single call. Ships with a reference terminal renderer; also supports a frontend handoff mode via Agno's `external_execution` pause/resume.

### Guardrails

- **`ContentModerationGuardrail`** — LLM-powered content moderation that blocks harmful or inappropriate input.
- **`AgenticPolicyGuardrail`** — LLM-powered policy enforcement that validates input against custom rules.
- **`MaxInputLengthGuardrail`** — Simple length check that rejects inputs exceeding a configurable character limit.

### Hooks

- **`create_logging_hooks`** — Factory that returns tool hooks for structured logging of every tool call.
- **`create_rate_limit_hook`** — Token-bucket rate limiter that raises `RateLimitExceeded` when limits are hit.

### Skills

- **`load_skills`** — Load bundled skill definitions (data-analysis, visualizer) for Agno agents.

## Quick Start

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from multek_agno import (
    AskUserQuestionsToolkit,
    VisualizerToolkit,
    ContentModerationGuardrail,
    MaxInputLengthGuardrail,
    create_logging_hooks,
    create_rate_limit_hook,
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        VisualizerToolkit(output_dir="./widgets"),
        AskUserQuestionsToolkit(),
    ],
    input_guardrails=[
        MaxInputLengthGuardrail(max_length=5000),
        ContentModerationGuardrail(),
    ],
    tool_hooks=[
        *create_logging_hooks(),
        create_rate_limit_hook(max_calls=20, window_seconds=60),
    ],
)
```

## `AskUserQuestionsToolkit`

Lets an agent pose 1–5 multiple-choice questions to the user and get their answers back as structured JSON. Each question has 2–4 options (the UI adds an "Other" free-text field automatically) and can be single-select (radio) or multi-select (checkbox) via `multi_select: bool`. Users can skip any question.

### Inline mode — terminal TUI (default)

Uses a built-in renderer based on `prompt_toolkit`. Requires the `[terminal]` extra.

```python
from multek_agno import AskUserQuestionsToolkit

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[AskUserQuestionsToolkit()],
)
agent.print_response("Help me pick a web framework for a small internal tool.")
# The agent will call ask_user_questions; the TUI pops up in your terminal.
```

Try the reference UI directly:

```bash
uv run python examples/ask_user_questions_demo.py
```

Keybindings: `↑`/`↓` navigate (down past the last option focuses "Outro…"), `1`-`4` jump to an option, `Enter` selects, `Space` toggles in multi-select, `Tab` focuses the free-text field, `Esc` skips, `Ctrl+C` aborts.

### Inline mode — custom renderer

Plug in any `QuestionRenderer` (sync or async). Sync renderers are offloaded to a worker thread under `agent.arun()`, so they don't block the event loop.

```python
from typing import List
from multek_agno import AskUserAnswer, AskUserQuestion, AskUserQuestionsToolkit

def my_renderer(questions: List[AskUserQuestion]) -> List[AskUserAnswer]:
    # ... render however you like (web, Telegram, voice, etc.) ...
    return [AskUserAnswer(question=q.question, user_answer=[q.options[0].title]) for q in questions]

toolkit = AskUserQuestionsToolkit(renderer=my_renderer)
```

### Frontend mode — `external_execution=True`

For a web/mobile frontend: the agent **pauses** before calling the tool. Your frontend reads the paused requirement, renders its own UI, and provides the answers via Agno's HITL protocol. No renderer is needed.

```python
toolkit = AskUserQuestionsToolkit(
    external_execution=True,
    external_execution_silent=True,  # suppress Agno's console "Run is paused..." panel
)

run_response = agent.run("Help me pick a material for my project.")

if run_response.is_paused:
    for requirement in run_response.active_requirements:
        if requirement.needs_external_execution and requirement.tool_execution.tool_name == "ask_user_questions":
            questions = requirement.tool_execution.tool_args["questions"]
            # Send `questions` to your frontend, collect the user's answers, then:
            answers_json = "[{...AskUserAnswer shape...}, ...]"
            requirement.set_external_execution_result(answers_json)

    run_response = agent.continue_run(run_id=run_response.run_id, requirements=run_response.requirements)
```

Return shape (one entry per question, in order):

```json
[
  {"question": "...", "user_answer": ["Option 2"], "other_text": null, "skipped": false},
  {"question": "...", "user_answer": [], "other_text": "Aço inox", "skipped": false},
  {"question": "...", "user_answer": [], "other_text": null, "skipped": true}
]
```

| Field           | Meaning                                                                    |
| --------------- | -------------------------------------------------------------------------- |
| `user_answer`   | Titles of the options the user picked (0..1 for radio, 0..n for checkbox). |
| `other_text`    | Free-text entered in the "Outro…" field; `null` when unused.               |
| `skipped`       | `true` when the user pressed Esc / "Pular"; both other fields are empty.   |

## `VisualizerToolkit`

Lets an agent produce a self-contained HTML document and hand it off for rendering. By default the tool runs in-process and returns a JSON payload (`{title, description, html, file_path}`); optionally it can also persist the HTML to disk via `output_dir`.

For frontend integrations, set `external_execution=True` and the agent will pause before the tool runs so your frontend can render the HTML itself (e.g. inside a sandboxed iframe).

```python
toolkit = VisualizerToolkit(
    external_execution=True,
    external_execution_silent=True,  # suppress Agno's stdout "Run is paused..." panel
)

run_response = agent.run("Plot the last 12 months of revenue.")

if run_response.is_paused:
    for requirement in run_response.active_requirements:
        if requirement.needs_external_execution and requirement.tool_execution.tool_name == "create_html_widget":
            args = requirement.tool_execution.tool_args
            html = args["html_content"]  # full self-contained HTML document
            title = args["title"]
            description = args["description"]
            # Render `html` in your frontend. When done, echo a result back:
            result_json = '{"rendered": true}'  # or any string you want the LLM to read
            requirement.set_external_execution_result(result_json)

    run_response = agent.continue_run(run_id=run_response.run_id, requirements=run_response.requirements)
```

`output_dir` is only valid in inline mode — passing it together with `external_execution=True` raises `ValueError`, since the tool body never runs when external execution is on.

## Development

```bash
# Install with dev dependencies
uv sync

# Run tests
pytest

# Lint & format
ruff check .
ruff format .

# Type check
mypy src/
```

## License

MIT
