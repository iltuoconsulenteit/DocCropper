import os

from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_app = get_asgi_application()

from services.api.app import app as fastapi_app

application = FastAPI()
application.mount('/api', fastapi_app)
application.mount('/', WSGIMiddleware(django_app))
