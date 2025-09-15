"""Tests for loading wiki content safely."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SPEC = importlib.util.spec_from_file_location(
    "wiki_content", ROOT / "services" / "api" / "wiki_content.py"
)
wiki_module = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(wiki_module)


def test_read_wiki_content_returns_html():
    html = wiki_module.read_wiki_content("it", "index.html")
    assert "<h1" in html


def test_read_wiki_content_defaults_to_index():
    html = wiki_module.read_wiki_content("it", "")
    assert "DocCropper" in html


def test_read_wiki_content_missing_page_raises():
    with pytest.raises(FileNotFoundError):
        wiki_module.read_wiki_content("it", "missing.html")


def test_read_wiki_content_prevents_traversal():
    with pytest.raises(FileNotFoundError):
        wiki_module.read_wiki_content("it", "../app.py")
