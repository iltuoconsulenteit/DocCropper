import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount
import logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

django_app = get_asgi_application()

from services.api.app import app as fastapi_app

# Build a Starlette application that serves Django at the root and the
# existing FastAPI application under the ``/api`` prefix.  ``/api`` must be
# registered before the Django catch‑all so requests to that path are handled
# by FastAPI rather than Django's URL resolver.  Defining the mounts up front
# avoids any ordering surprises during startup.
routes = [
    Mount("/api", fastapi_app),
    Mount("/", django_app),
]
application = Starlette(routes=routes)

logger = logging.getLogger("uvicorn.error")

@application.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Incoming %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("Completed %s %s with status %s", request.method, request.url.path, response.status_code)
    return response
