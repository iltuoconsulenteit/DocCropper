import os

from django.core.asgi import get_asgi_application
from starlette.applications import Starlette

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "platform.config.settings")

django_app = get_asgi_application()

from services.api.app import app as fastapi_app

# Build a Starlette application that serves Django at the root and the
# existing FastAPI application under the ``/api`` prefix.  ``/api`` must be
# mounted before the Django catch‑all so requests to that path are handled by
# FastAPI rather than Django's URL resolver.
application = Starlette()
application.mount("/api", fastapi_app)
application.mount("/", django_app)
