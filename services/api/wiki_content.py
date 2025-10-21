"""Helpers for loading bundled wiki content safely."""
from __future__ import annotations

from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parents[2] / "wiki"


def read_wiki_content(lang: str, page: str = "index.html") -> str:
    """Return the HTML contents of a wiki page.

    Parameters
    ----------
    lang:
        Language folder under the ``wiki`` directory. Defaults to ``it`` when
        empty.
    page:
        Page filename to read inside the language folder. ``index.html`` is
        used when empty. Any attempt to escape the wiki directory raises
        ``FileNotFoundError``.
    """
    lang = (lang or "").strip().lower() or "it"
    page = (page or "").strip() or "index.html"
    # Remove any leading directory separator so ``Path`` doesn't interpret the
    # page as an absolute path on Windows.
    page = page.lstrip("/\\")

    # Build the target path and ensure it lives inside the wiki root to guard
    # against path traversal attempts.
    root = WIKI_ROOT.resolve()
    candidate = (root / lang / page).resolve()

    try:
        candidate.relative_to(root)
    except ValueError as exc:  # pragma: no cover - defensive, but tested below
        raise FileNotFoundError(page) from exc

    if not candidate.is_file():
        raise FileNotFoundError(page)

    return candidate.read_text(encoding="utf-8")
