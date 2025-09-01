import os
import logging
from types import SimpleNamespace
from starlette.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

from django.core.asgi import get_asgi_application  # noqa: E402
from services.api.app import app as fastapi_app  # noqa: E402

logger = logging.getLogger("uvicorn.error")


def log_message(scope, status):
    logger.info(
        "Completed %s %s with status %s",
        scope.get("method"),
        scope.get("path"),
        status,
    )


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("Incoming %s %s", request.method, request.url.path)
        response = await call_next(request)
        return response


django_app = get_asgi_application()
fastapi_app.add_middleware(LogMiddleware)

django_app = LogMiddleware(django_app)


class Dispatcher:
    def __init__(self, django_app, fastapi_app):
        self.django_app = django_app
        self.fastapi_app = fastapi_app
        self.state = SimpleNamespace()

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        if path == "/openapi.json":
            response = RedirectResponse("/api/openapi.json")
            await response(scope, receive, send)
            log_message(scope, response.status_code)
            return
        if path.startswith("/api"):
            scope = dict(scope)
            scope["root_path"] = "/api"
            scope["path"] = path[4:] or "/"
            await self.fastapi_app(scope, receive, send)
        else:
            await self.django_app(scope, receive, send)


application = Dispatcher(django_app, fastapi_app)
