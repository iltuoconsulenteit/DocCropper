import os
import logging
from typing import Callable, Awaitable, Dict, Any
from types import SimpleNamespace

from django.core.asgi import get_asgi_application

# Ensure Django settings are loaded before importing the Django application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

django_app = get_asgi_application()

from services.api.app import app as fastapi_app  # noqa: E402

logger = logging.getLogger("uvicorn.error")


async def application(scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
    """ASGI dispatcher that routes /api to FastAPI and everything else to Django."""
    if scope["type"] not in {"http", "websocket"}:
        await django_app(scope, receive, send)
        return

    path = scope.get("path", "")
    method = scope.get("method", "")
    status_code = 500

    async def send_wrapper(message: Dict[str, Any]) -> None:
        nonlocal status_code
        if message["type"] == "http.response.start":
            status_code = message["status"]
        await send(message)

    logger.info("Incoming %s %s", method, path)
    if path.startswith("/api"):
        scope_api = dict(scope)
        scope_api["path"] = path[4:] or "/"
        scope_api["root_path"] = "/api"
        await fastapi_app(scope_api, receive, send_wrapper)
    elif path == "/openapi.json":
        # Swagger UI, served at /api/docs, requests the OpenAPI schema from
        # the root path. Forward this standalone request to the FastAPI app
        # without stripping the leading slash so the schema is returned
        # correctly.
        scope_api = dict(scope)
        await fastapi_app(scope_api, receive, send_wrapper)
    else:
        await django_app(scope, receive, send_wrapper)
    logger.info("Completed %s %s with status %s", method, path, status_code)


# allow external consumers (e.g. main.py) to attach server references
application.state = SimpleNamespace()
