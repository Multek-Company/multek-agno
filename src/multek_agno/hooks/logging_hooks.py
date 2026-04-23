"""Logging hooks — pre/post hooks that log tool calls with timing information."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, Optional, Tuple

from agno.tools import FunctionCall

logger = logging.getLogger("multek_agno.hooks")


def create_logging_hooks(
    log_level: int = logging.INFO,
    log_arguments: bool = True,
    log_result: bool = False,
    custom_logger: Optional[logging.Logger] = None,
) -> Tuple[Callable[[FunctionCall], None], Callable[[FunctionCall], None]]:
    """Create a pair of pre/post hooks that log tool calls with timing.

    Args:
        log_level: Logging level (default ``logging.INFO``).
        log_arguments: Whether to include function arguments in the log.
        log_result: Whether to include the function result in the post-hook log.
        custom_logger: Optional logger instance. Defaults to ``multek_agno.hooks``.

    Returns:
        A ``(pre_hook, post_hook)`` tuple to pass to the ``@tool`` decorator.

    Example::

        from agno.tools import tool
        from multek_agno.hooks import create_logging_hooks

        pre, post = create_logging_hooks(log_result=True)

        @tool(pre_hook=pre, post_hook=post)
        def my_tool(query: str) -> str:
            return f"result for {query}"
    """
    _logger = custom_logger or logger
    _timings: dict[str, float] = {}

    def pre_hook(fc: FunctionCall) -> None:
        name = fc.function.name
        _timings[name] = time.monotonic()
        parts = [f"Tool call: {name}"]
        if log_arguments and fc.arguments:
            parts.append(f"args={fc.arguments}")
        _logger.log(log_level, " | ".join(parts))

    def post_hook(fc: FunctionCall) -> None:
        name = fc.function.name
        elapsed = time.monotonic() - _timings.pop(name, time.monotonic())
        parts = [f"Tool done: {name}", f"elapsed={elapsed:.3f}s"]
        if log_result and fc.result is not None:
            result_str = str(fc.result)
            if len(result_str) > 200:
                result_str = result_str[:200] + "..."
            parts.append(f"result={result_str}")
        _logger.log(log_level, " | ".join(parts))

    return pre_hook, post_hook
