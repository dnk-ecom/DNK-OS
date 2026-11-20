# --- DNK-MRH-HEADER ---
# mrh_id: "tests/core/test_dnk_native_system.py"
# purpose: "Unit tests for native lightweight macOS computer use and two-tier web engine (DEC-148)"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-18"
# author: "DNK-e.com"
# --- END DNK-MRH-HEADER ---

import subprocess
import sys
from pathlib import Path

import pytest
from scripts.system.dnk_browser import _SimpleHTMLTextExtractor
from scripts.system.dnk_computer_use import get_screen_size, get_frontmost_app


def test_simple_html_text_extractor():
    extractor = _SimpleHTMLTextExtractor()
    sample_html = """
    <html>
        <head><title>Test Page Title</title></head>
        <body>
            <script>var x = 10;</script>
            <style>body { color: red; }</style>
            <h1>Main Heading</h1>
            <p>This is a paragraph with <a href="https://example.com">a link</a>.</p>
        </body>
    </html>
    """
    extractor.feed(sample_html)
    text = extractor.get_markdown()

    assert extractor.title == "Test Page Title"
    assert "Main Heading" in text
    assert "This is a paragraph with a link" in text
    assert "var x = 10;" not in text
    assert "color: red" not in text


def test_dnk_computer_use_screen_size():
    size = get_screen_size()
    assert isinstance(size, dict)
    assert "width" in size
    assert "height" in size
    assert size["width"] > 0
    assert size["height"] > 0


def test_dnk_computer_use_frontmost_app():
    app = get_frontmost_app()
    assert isinstance(app, str)
    assert len(app) > 0


def test_dnk_browser_cli_fetch():
    res = subprocess.run(
        [sys.executable, "scripts/system/dnk_browser.py", "fetch", "https://example.com"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0
    assert "Example Domain" in res.stdout
