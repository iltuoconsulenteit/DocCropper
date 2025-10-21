from django.shortcuts import render
from django.http import FileResponse, Http404
from django.utils._os import safe_join
from pathlib import Path
import mimetypes
import os


def home(request):
    """Render the main portal page using the Expressive template."""
    return render(request, 'expressive/index.html')


ROOT_DIR = Path(__file__).resolve().parents[3]
WIKI_DIR = ROOT_DIR / "wiki"


def wiki(request, path="index.html"):
    """Serve wiki assets without caching so help pages always load."""
    if not path:
        path = "index.html"
    fullpath = safe_join(str(WIKI_DIR), path)
    if not os.path.exists(fullpath):
        raise Http404("Page not found")
    content_type, _ = mimetypes.guess_type(fullpath)
    response = FileResponse(open(fullpath, "rb"), content_type=content_type)
    response["Cache-Control"] = "no-store, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response.headers.pop("X-Frame-Options", None)
    response["Content-Security-Policy"] = "frame-ancestors *"
    return response
