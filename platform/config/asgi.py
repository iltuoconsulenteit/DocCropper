import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

django_app = get_asgi_application()

from services.api.app import app as fastapi_app

application = Starlette()
application.mount("/api", fastapi_app)
application.mount("/", django_app)
# Ensure the API mount takes precedence over the catch-all Django route
application.router.routes.sort(key=lambda r: getattr(r, "path", ""), reverse=True)
