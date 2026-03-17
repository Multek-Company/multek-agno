# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**multek-agno** is a Python package providing reusable, shared components for the [Agno Agents SDK](https://docs.agno.com). It extends Agno with custom toolkits, guardrails, hooks, and other agent building blocks that can be installed and used across multiple Agno-based projects.

## Agno SDK Key Concepts

- **Toolkits**: Classes inheriting `agno.tools.Toolkit`. Register tool functions in the constructor via `self.register(self.method)` or pass them as a `tools` list to `super().__init__()`.
- **Guardrails**: Classes inheriting `agno.guardrails.base.BaseGuardrail`. Implement `check(run_input)` and `async_check(run_input)`. Raise `agno.exceptions.InputCheckError` to block requests. Attached to agents via `pre_hooks=[]`.
- **Tool Hooks**: Standalone functions with signature `(function_name: str, function_call: Callable, arguments: Dict[str, Any])` or `(run_context: RunContext, function_call: Callable, arguments: Dict[str, Any])`. Attached via `tool_hooks=[]`. Must call `function_call(**arguments)` and return the result.
- **RunContext / session_state**: Hooks and tools can access `run_context.session_state` for shared state across the agent run.

## Build & Development Commands

```bash
# Install dependencies (using uv — preferred)
uv sync

# Install in editable mode
uv pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_<name>.py

# Run a specific test
pytest tests/test_<name>.py::test_function_name -v

# Lint
ruff check .

# Format
ruff format .

# Type checking
mypy src/
```

## Architecture

```
src/
  multek_agno/
    toolkits/       # Custom Toolkit classes (extend agno.tools.Toolkit)
    guardrails/     # Custom guardrail classes (extend agno.guardrails.base.BaseGuardrail)
    hooks/          # Reusable tool hook functions
tests/              # Mirrors src structure
```

### Conventions

- Each toolkit, guardrail, or hook should be a standalone module that can be imported independently.
- Toolkits register their tools in `__init__` and should include docstrings with `Args`/`Returns` — Agno uses these docstrings as the tool schema for the LLM.
- Guardrails must implement both `check()` (sync) and `async_check()` (async) methods.
- All components should work with any Agno-supported model provider (OpenAI, Google, Anthropic, etc.) — avoid provider-specific logic unless the component is explicitly provider-scoped.
