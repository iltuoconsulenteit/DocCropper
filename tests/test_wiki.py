"""Test the ASGI dispatcher routes wiki requests to the FastAPI app."""

import sys
import types
import asyncio
from pathlib import Path

# Ensure project root on path for local imports
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Stub modules required by platform.config.asgi so we don't need the full
# Django/Starlette/FastAPI stack during tests.
class DummyRedirectResponse:
    def __init__(self, url):
        self.url = url
        self.status_code = 200
    async def __call__(self, scope, receive, send):
        pass

starlette_module = types.ModuleType("starlette")
responses_module = types.ModuleType("starlette.responses")
responses_module.RedirectResponse = DummyRedirectResponse
starlette_module.responses = responses_module
sys.modules["starlette"] = starlette_module
sys.modules["starlette.responses"] = responses_module

def dummy_get_asgi_application():
    async def app(scope, receive, send):
        pass
    return app

django_module = types.ModuleType("django")
core_module = types.ModuleType("django.core")
asgi_module = types.ModuleType("django.core.asgi")
asgi_module.get_asgi_application = dummy_get_asgi_application
exceptions_module = types.ModuleType("django.core.exceptions")

class RequestAborted(Exception):
    pass

exceptions_module.RequestAborted = RequestAborted

sys.modules["django"] = django_module
sys.modules["django.core"] = core_module
sys.modules["django.core.asgi"] = asgi_module
sys.modules["django.core.exceptions"] = exceptions_module

# Stub the FastAPI app module
fastapi_called = {}
async def fastapi_app(scope, receive, send):
    fastapi_called["path"] = scope.get("path")

services_module = types.ModuleType("services")
api_module = types.ModuleType("services.api")
app_module = types.ModuleType("services.api.app")
app_module.app = fastapi_app
sys.modules["services"] = services_module
sys.modules["services.api"] = api_module
sys.modules["services.api.app"] = app_module

# Remove standard 'platform' so our local package can be imported
sys.modules.pop("platform", None)

from platform.config.asgi import Dispatcher  # noqa: E402


def test_wiki_routed_to_fastapi():
    async def dummy_django(scope, receive, send):
        pass

    dispatcher = Dispatcher(dummy_django, fastapi_app)

    async def receive():
        return {}

    async def send(message):
        pass

    asyncio.run(dispatcher({"path": "/wiki/it/index.html", "method": "GET"}, receive, send))
    assert fastapi_called["path"] == "/wiki/it/index.html"


def test_wiki_mount_present():
    content = Path("services/api/app.py").read_text()
    assert 'NoCacheStaticFiles(directory=str(WIKI_DIR), html=True)' in content
