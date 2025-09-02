from django.apps import AppConfig
import os


def _ensure_default_admin():
    """Create a default superuser if none exists."""
    from django.contrib.auth import get_user_model
    from django.db.utils import OperationalError

    try:
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
            password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin")
            User.objects.create_superuser(username=username, email="", password=password)
    except OperationalError:
        # Database might not be ready (e.g. during migrations)
        pass


class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'platform.apps.portal'

    def ready(self):
        _ensure_default_admin()
