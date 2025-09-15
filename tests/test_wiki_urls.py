from pathlib import Path


def test_django_url_pattern_includes_wiki():
    content = Path("platform/config/urls.py").read_text()
    assert "re_path(r'^wiki" in content
