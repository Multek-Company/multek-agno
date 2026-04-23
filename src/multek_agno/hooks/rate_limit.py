"""Rate-limit hook — a pre-hook that enforces per-tool call frequency limits."""

from __future__ import annotations

import time
from typing import Dict, Optional

from agno.tools import FunctionCall


class RateLimitExceeded(Exception):
    """Raised when a tool call exceeds the configured rate limit."""

    def __init__(self, tool_name: str, retry_after: float) -> None:
        self.tool_name = tool_name
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for '{tool_name}'. Retry after {retry_after:.1f}s.")


def create_rate_limit_hook(
    max_calls: int = 10,
    window_seconds: float = 60.0,
    per_tool: bool = True,
) -> callable:
    """Create a pre-hook that enforces a sliding-window rate limit on tool calls.

    Args:
        max_calls: Maximum number of calls allowed within the window.
        window_seconds: Time window in seconds.
        per_tool: If True, each tool has its own counter. If False, all tools share one.

    Returns:
        A pre-hook function to pass to the ``@tool`` decorator.

    Raises:
        RateLimitExceeded: When a call would exceed the limit.

    Example::

        from agno.tools import tool
        from multek_agno.hooks import create_rate_limit_hook

        limiter = create_rate_limit_hook(max_calls=5, window_seconds=60)

        @tool(pre_hook=limiter)
        def search(query: str) -> str:
            return f"results for {query}"
    """
    _call_log: Dict[Optional[str], list[float]] = {}

    def pre_hook(fc: FunctionCall) -> None:
        key = fc.function.name if per_tool else None
        now = time.monotonic()
        timestamps = _call_log.setdefault(key, [])

        # Prune expired entries
        cutoff = now - window_seconds
        _call_log[key] = [t for t in timestamps if t > cutoff]
        timestamps = _call_log[key]

        if len(timestamps) >= max_calls:
            oldest = timestamps[0]
            retry_after = oldest + window_seconds - now
            raise RateLimitExceeded(fc.function.name, retry_after)

        timestamps.append(now)

    return pre_hook
