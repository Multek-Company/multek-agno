"""Instructions template and helpers injected into the agent's system prompt."""

from __future__ import annotations

from typing import List, Optional

from multek_agno._utils.html import CDN_URLS

DEFAULT_INSTRUCTIONS = """\
You have access to a tool called `create_html_widget` that renders interactive HTML widgets \
directly to the user. Use it whenever the user asks for a visualization, chart, diagram, \
interactive tool, calculator, game, or any UI that benefits from HTML/CSS/JS.

## How to use create_html_widget

- **html_content**: A complete, self-contained HTML document (including `<!DOCTYPE html>`, \
`<html>`, `<head>`, `<body>` tags). All CSS and JS must be inlined or loaded from CDN.
- **title**: A short, descriptive title for the widget.
- **description**: A one-sentence description of what the widget does.

## Best Practices

1. Write a **single, complete HTML file** — do not split into multiple files.
2. Use **inline `<style>` and `<script>` tags** for all CSS and JS.
3. Make widgets **responsive** — use relative units, flexbox, or grid.
4. Add **smooth animations and transitions** for a polished feel.
5. Use **modern CSS** (variables, gradients, backdrop-filter, etc.).
6. Handle **edge cases** gracefully (empty states, errors, loading).
7. Prefer **vanilla JS** unless a library adds clear value.

## Available CDN Libraries

You may include these via `<script>` or `<link>` tags:

{cdn_list}

You can also use any other publicly available CDN library if needed.
"""


def format_cdn_list(allowed: Optional[List[str]]) -> str:
    """Build a markdown list of CDN libraries for the instructions."""
    if allowed is not None:
        urls = {k: v for k, v in CDN_URLS.items() if k in allowed}
    else:
        urls = CDN_URLS

    if not urls:
        return "No specific CDN libraries are pre-configured, but you may use any public CDN."

    lines: list[str] = []
    for name, url in urls.items():
        lines.append(f"- **{name}**: `{url}`")
    return "\n".join(lines)
