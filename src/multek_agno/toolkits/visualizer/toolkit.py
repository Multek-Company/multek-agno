"""The `VisualizerToolkit` — lets an agent generate interactive HTML/CSS/JS widgets."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from agno.tools.toolkit import Toolkit

from multek_agno._utils.html import slugify

from .prompt import DEFAULT_INSTRUCTIONS, format_cdn_list


class VisualizerToolkit(Toolkit):
    """Toolkit that lets an Agno agent generate interactive HTML/CSS/JS widgets.

    The toolkit has two modes:

    - **Inline mode (default, `external_execution=False`)**: the tool runs in-process.
      If `output_dir` is set, the HTML file is written to disk. The tool returns a JSON
      blob with the title, description, html, and file_path — the calling layer decides
      how to render it (e.g. pipe it to a webview, email it, log it).

    - **External-execution mode (`external_execution=True`)**: the agent pauses before
      calling the tool. Your frontend/client reads the paused run's
      `tool_args` (`html_content`, `title`, `description`), renders the HTML itself
      (e.g. inside a sandboxed iframe), and resumes the run via
      `requirement.set_external_execution_result(json_string)` +
      `agent.continue_run(...)`. Writing to disk (`output_dir`) is disabled in this
      mode because the tool body never executes; passing both raises `ValueError`.

    Args:
        output_dir: If set, HTML files are also saved to this directory. Only valid in
            inline mode.
        allowed_cdn_libs: Optional list of CDN library keys to advertise to the LLM.
            If None, all libraries in CDN_URLS are advertised.
        external_execution: When True, the tool pauses the agent so an external system
            (e.g. a web frontend) renders the HTML. Mutually exclusive with `output_dir`.
        external_execution_silent: When True, suppresses Agno's verbose
            "Run is paused..." console output. Only meaningful alongside
            `external_execution=True`; passing it with inline mode raises `ValueError`.
    """

    def __init__(
        self,
        output_dir: Optional[str] = None,
        allowed_cdn_libs: Optional[List[str]] = None,
        external_execution: bool = False,
        external_execution_silent: bool = False,
    ) -> None:
        if external_execution and output_dir is not None:
            raise ValueError(
                "external_execution=True is incompatible with output_dir. "
                "In external-execution mode the tool body never runs, so there is "
                "nothing to write to disk — the frontend is responsible for persisting "
                "the HTML if needed."
            )
        if external_execution_silent and not external_execution:
            raise ValueError(
                "external_execution_silent=True requires external_execution=True. "
                "The flag only affects the pause-output console formatting, which "
                "is only produced when the tool actually pauses."
            )

        self.output_dir = output_dir
        self.allowed_cdn_libs = allowed_cdn_libs
        self.external_execution: bool = external_execution
        self.external_execution_silent: bool = external_execution_silent

        instructions = DEFAULT_INSTRUCTIONS.format(cdn_list=format_cdn_list(allowed_cdn_libs))

        super().__init__(
            name="visualizer",
            tools=[self.create_html_widget],
            instructions=instructions,
            add_instructions=True,
            show_result_tools=["create_html_widget"],
            stop_after_tool_call_tools=["create_html_widget"],
            external_execution_required_tools=(["create_html_widget"] if external_execution else []),
        )

        # `Toolkit` doesn't take an `external_execution_silent_tools` list, so we
        # set the flag on the underlying `Function` objects after registration.
        # Agno reads `fc.function.external_execution_silent` when building the
        # paused ToolExecution (see agno/models/base.py) and when deciding whether
        # to render the "Run is paused..." panel (see agno/utils/response.py).
        if external_execution_silent:
            for fn_dict in (self.functions, self.async_functions):
                fn = fn_dict.get("create_html_widget")
                if fn is not None:
                    fn.external_execution_silent = True

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
        if self.external_execution:
            raise RuntimeError(
                "create_html_widget should not execute when external_execution=True; "
                "Agno is expected to pause before calling this tool so your frontend "
                "can render the HTML and provide the result via "
                "requirement.set_external_execution_result(). "
                "If you're seeing this error, the pause machinery is not wired up."
            )

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
