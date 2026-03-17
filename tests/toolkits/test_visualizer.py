"""Tests for VisualizerToolkit."""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from multek_agno._utils.html import CDN_URLS, slugify
from multek_agno.toolkits.visualizer import VisualizerToolkit

# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("Hello World", "hello-world"),
        ("My Chart!!", "my-chart"),
        ("  spaces  everywhere  ", "spaces-everywhere"),
        ("über-cool-widget", "uber-cool-widget"),
        ("already-slugged", "already-slugged"),
        ("UPPER CASE", "upper-case"),
        ("dots.and...more", "dotsandmore"),
        ("", ""),
    ],
)
def test_slugify(input_text: str, expected: str) -> None:
    assert slugify(input_text) == expected


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def test_toolkit_registers_create_html_widget() -> None:
    toolkit = VisualizerToolkit()
    assert "create_html_widget" in toolkit.functions


def test_toolkit_show_result_and_stop_after() -> None:
    toolkit = VisualizerToolkit()
    func = toolkit.functions["create_html_widget"]
    assert func.show_result is True
    assert func.stop_after_tool_call is True


def test_toolkit_has_instructions() -> None:
    toolkit = VisualizerToolkit()
    assert toolkit.instructions is not None
    assert "create_html_widget" in toolkit.instructions


# ---------------------------------------------------------------------------
# create_html_widget — no output_dir
# ---------------------------------------------------------------------------

SAMPLE_HTML = "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hi</h1></body></html>"


def test_create_widget_returns_json() -> None:
    toolkit = VisualizerToolkit()
    result_str = toolkit.create_html_widget(
        html_content=SAMPLE_HTML,
        title="Test Widget",
        description="A test widget",
    )
    result = json.loads(result_str)
    assert result["title"] == "Test Widget"
    assert result["description"] == "A test widget"
    assert result["html"] == SAMPLE_HTML
    assert result["file_path"] is None


# ---------------------------------------------------------------------------
# create_html_widget — with output_dir
# ---------------------------------------------------------------------------


def test_create_widget_saves_file() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        toolkit = VisualizerToolkit(output_dir=tmpdir)
        result_str = toolkit.create_html_widget(
            html_content=SAMPLE_HTML,
            title="My Dashboard",
            description="A dashboard",
        )
        result = json.loads(result_str)

        assert result["file_path"] is not None
        assert os.path.isfile(result["file_path"])
        assert result["file_path"].endswith("my-dashboard.html")

        with open(result["file_path"], encoding="utf-8") as f:
            assert f.read() == SAMPLE_HTML


def test_create_widget_creates_output_dir_if_missing() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        nested = os.path.join(tmpdir, "sub", "dir")
        toolkit = VisualizerToolkit(output_dir=nested)
        toolkit.create_html_widget(
            html_content=SAMPLE_HTML,
            title="Nested",
            description="test",
        )
        assert os.path.isdir(nested)


def test_create_widget_no_file_when_output_dir_none() -> None:
    toolkit = VisualizerToolkit(output_dir=None)
    result_str = toolkit.create_html_widget(
        html_content=SAMPLE_HTML,
        title="No Save",
        description="test",
    )
    result = json.loads(result_str)
    assert result["file_path"] is None


# ---------------------------------------------------------------------------
# CDN URLs
# ---------------------------------------------------------------------------


def test_cdn_urls_not_empty() -> None:
    assert len(CDN_URLS) > 0
    assert "chartjs" in CDN_URLS
    assert "d3" in CDN_URLS


# ---------------------------------------------------------------------------
# allowed_cdn_libs filtering
# ---------------------------------------------------------------------------


def test_allowed_cdn_libs_filters_instructions() -> None:
    toolkit = VisualizerToolkit(allowed_cdn_libs=["chartjs", "d3"])
    assert toolkit.instructions is not None
    assert "chartjs" in toolkit.instructions
    assert "d3" in toolkit.instructions
    assert "threejs" not in toolkit.instructions


def test_allowed_cdn_libs_none_shows_all() -> None:
    toolkit = VisualizerToolkit(allowed_cdn_libs=None)
    assert toolkit.instructions is not None
    for key in CDN_URLS:
        assert key in toolkit.instructions
