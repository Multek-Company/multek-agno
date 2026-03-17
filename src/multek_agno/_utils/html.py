"""HTML helpers for the Visualizer toolkit."""

import re
import unicodedata

CDN_URLS: dict[str, str] = {
    "chartjs": "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js",
    "d3": "https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js",
    "plotly": "https://cdn.plot.ly/plotly-latest.min.js",
    "threejs": "https://cdn.jsdelivr.net/npm/three@0.160/build/three.min.js",
    "leaflet_js": "https://unpkg.com/leaflet@1/dist/leaflet.js",
    "leaflet_css": "https://unpkg.com/leaflet@1/dist/leaflet.css",
    "tailwindcss": "https://cdn.tailwindcss.com",
    "katex_js": "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js",
    "katex_css": "https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css",
    "mermaid": "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js",
}


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug.

    Args:
        text: The text to slugify.

    Returns:
        A lowercase, hyphen-separated, ASCII-safe string.
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    return text.strip("-")
