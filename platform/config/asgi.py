import os
import logging
from types import SimpleNamespace
from starlette.responses import RedirectResponse
from django.core.exceptions import RequestAborted

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

from django.core.asgi import get_asgi_application  # noqa: E402
from services.api.app import app as fastapi_app  # noqa: E402

logger = logging.getLogger("uvicorn.error")

django_app = get_asgi_application()


class Dispatcher:
    def __init__(self, django_app, fastapi_app):
        self.django_app = django_app
        self.fastapi_app = fastapi_app
        self.state = SimpleNamespace()

    async def __call__(self, scope, receive, send):
        path = scope.get("path", "")
        logger.info("Incoming %s %s", scope.get("method"), path)
        if path == "/openapi.json":
            response = RedirectResponse("/api/openapi.json")
            await response(scope, receive, send)
            logger.info(
                "Completed %s %s with status %s",
                scope.get("method"),
                path,
                response.status_code,
            )
            return
        if path.startswith("/api"):
            scope = dict(scope)
            scope["root_path"] = "/api"
            scope["path"] = path[4:] or "/"
            await self.fastapi_app(scope, receive, send)
            return
        if path == "/sign" or path.startswith(
            (
                "/sign/",
                "/start-sign",
                "/sign-pages",
                "/submit-signature",
                "/finish-signing",
                "/signature-result",
                "/store-signed-pdf",
            )
        ):
            await self.fastapi_app(scope, receive, send)
            return
        if path.startswith("/wiki"):
            await self.fastapi_app(scope, receive, send)
            return
        try:
            await self.django_app(scope, receive, send)
        except RequestAborted:
            logger.info("Client disconnected before response for %s", path)
            return
        logger.info("Completed %s %s with status 200", scope.get("method"), path)


application = Dispatcher(django_app, fastapi_app)
