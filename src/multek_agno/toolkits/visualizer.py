"""VisualizerToolkit — lets agents generate interactive HTML/CSS/JS widgets inline."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from agno.tools.toolkit import Toolkit

from multek_agno._utils.html import CDN_URLS, slugify

_DEFAULT_INSTRUCTIONS = """\
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


def _format_cdn_list(allowed: Optional[List[str]]) -> str:
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


class VisualizerToolkit(Toolkit):
    """Toolkit that lets an Agno agent generate interactive HTML/CSS/JS widgets.

    Args:
        output_dir: If set, HTML files are also saved to this directory.
        allowed_cdn_libs: Optional list of CDN library keys to advertise to the LLM.
            If None, all libraries in CDN_URLS are advertised.
    """

    def __init__(
        self,
        output_dir: Optional[str] = None,
        allowed_cdn_libs: Optional[List[str]] = None,
    ) -> None:
        self.output_dir = output_dir
        self.allowed_cdn_libs = allowed_cdn_libs

        instructions = _DEFAULT_INSTRUCTIONS.format(cdn_list=_format_cdn_list(allowed_cdn_libs))

        super().__init__(
            name="visualizer",
            tools=[self.create_html_widget],
            instructions=instructions,
            add_instructions=True,
            show_result_tools=["create_html_widget"],
            stop_after_tool_call_tools=["create_html_widget"],
        )

    def create_html_widget(self, html_content: str, title: str, description: str) -> str:
        """Create an interactive HTML widget and return it for display.

        Use this tool to generate self-contained HTML documents with interactive
        visualizations, charts, diagrams, calculators, games, or any UI component.

        Args:
            html_content: A complete, self-contained HTML document string including
                DOCTYPE, html, head, and body tags with all CSS/JS inlined or loaded from CDN.
            title: A short, descriptive title for the widget.
            description: A one-sentence description of what the widget does.

        Returns:
            A JSON string containing the widget title, description, HTML content,
            and optionally the file path where it was saved.
        """
        file_path: Optional[str] = None

        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)
            filename = f"{slugify(title)}.html"
            full_path = Path(self.output_dir) / filename
            full_path.write_text(html_content, encoding="utf-8")
            file_path = str(full_path)

        result = {
            "title": title,
            "description": description,
            "html": html_content,
            "file_path": file_path,
        }
        return json.dumps(result)
