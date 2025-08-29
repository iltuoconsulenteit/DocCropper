import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette
from starlette.routing import Mount

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

django_app = get_asgi_application()

from services.api.app import app as fastapi_app

routes = [
    Mount("/api", fastapi_app),
    Mount("/", django_app),
]

application = Starlette(routes=routes)
