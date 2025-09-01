import os
import logging
from types import SimpleNamespace

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.routing import Route

# Configure Django settings and create the Django ASGI app
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")
django_app = get_asgi_application()

# Import the existing FastAPI application
from services.api.app import app as fastapi_app  # noqa: E402

logger = logging.getLogger("uvicorn.error")


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info("Incoming %s %s", request.method, request.url.path)
        response = await call_next(request)
        logger.info(
            "Completed %s %s with status %s",
            request.method,
            request.url.path,
            response.status_code,
        )
        return response


# Starlette application that mounts FastAPI at /api and Django everywhere else


async def _openapi_forward(request: Request) -> RedirectResponse:
    """Expose FastAPI's OpenAPI schema at ``/openapi.json``.

    The Swagger UI served from ``/api/docs`` expects the schema at the root
    path, so we forward such requests to the FastAPI application.
    """

    return RedirectResponse("/api/openapi.json")


routes = [Route("/openapi.json", _openapi_forward)]

application = Starlette(routes=routes)
application.mount("/api", fastapi_app)
application.mount("/", django_app)
application.add_middleware(LogMiddleware)

# allow external consumers (e.g. main.py) to attach server references
application.state = SimpleNamespace()
