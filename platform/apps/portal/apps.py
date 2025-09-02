from django.apps import AppConfig
from django.db.models.signals import post_migrate
import os


def _ensure_default_admin():
    """Create a default superuser if none exists."""
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError, ProgrammingError

    try:
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
            password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")
            User.objects.create_superuser(username=username, email="", password=password)
    except (OperationalError, ProgrammingError):
        # Database might not be ready (e.g. during migrations)
        pass


def _create_admin_post_migrate(**kwargs):
    _ensure_default_admin()


class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'platform.apps.portal'

    def ready(self):
        post_migrate.connect(_create_admin_post_migrate, sender=self)
        _ensure_default_admin()
