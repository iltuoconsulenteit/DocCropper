from pathlib import Path

def test_django_url_patterns_include_mobilesign_redirects():
    content = Path("platform/config/urls.py").read_text()
    assert "RedirectView" in content
    assert "sign-pages" in content
    assert "submit-signature" in content
