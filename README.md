# multek-agno

Reusable toolkits, guardrails, hooks, and skills for the [Agno Agents SDK](https://docs.agno.com).

## Installation

```bash
pip install multek-agno
```

## What's Included

### Toolkits

- **`VisualizerToolkit`** — Lets agents generate interactive HTML/CSS/JS widgets inline, with optional file output and CDN library support.

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
    VisualizerToolkit,
    ContentModerationGuardrail,
    MaxInputLengthGuardrail,
    create_logging_hooks,
    create_rate_limit_hook,
)

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[VisualizerToolkit(output_dir="./widgets")],
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
