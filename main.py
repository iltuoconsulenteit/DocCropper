import argparse
import importlib.util
import os
import signal
import sys
import tempfile
from pathlib import Path

import uvicorn
from types import SimpleNamespace

# Ensure the third-party `bcrypt` package exposes the ``__about__`` attribute
# expected by Passlib, even on newer releases where it was removed.
import bcrypt as _bcrypt

if not hasattr(_bcrypt, "__about__"):
    _bcrypt.__about__ = SimpleNamespace(
        __version__=getattr(_bcrypt, "__version__", "")
    )

BASE_DIR = Path(__file__).resolve().parent
platform_root = BASE_DIR / "platform"
spec = importlib.util.spec_from_file_location(
    "platform", platform_root / "__init__.py", submodule_search_locations=[str(platform_root)]
)
platform_pkg = importlib.util.module_from_spec(spec)
sys.modules["platform"] = platform_pkg
spec.loader.exec_module(platform_pkg)

try:
    import setproctitle
    setproctitle.setproctitle("DocCropper")
except Exception:
    try:  # Fallback for platforms where setproctitle is unavailable
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("DocCropper")
    except Exception:
        pass

from platform.config.asgi import application
from services.api.app import app as fastapi_app, load_settings, DEV_LICENSE_KEY_UPPER
from django.core.management import call_command

PID_FILE = os.path.join(tempfile.gettempdir(), 'doccropper.pid')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run or control DocCropper")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--stop", action="store_true", help="Stop a running instance")
    args = parser.parse_args()

    if args.stop:
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE) as fh:
                    pid = int(fh.read().strip())
                os.kill(pid, signal.SIGTERM)
                print(f"Stopped DocCropper (PID {pid})")
                os.remove(PID_FILE)
            except Exception as e:
                print(f"Failed to stop server: {e}")
        else:
            print("PID file not found. Server may not be running.")
        raise SystemExit

    try:
        call_command('migrate', run_syncdb=True, interactive=False, verbosity=0)
    except Exception as e:
        print(f"Database migration failed: {e}")

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
    except Exception as e:
        print(f"Failed to ensure admin user: {e}")

    settings = load_settings()
    port = args.port if args.port is not None else int(settings.get('port', 8765))
    host = args.host
    if settings.get('license_level', 'free').lower() != 'full':
        dev_env = DEV_LICENSE_KEY_UPPER
        key = settings.get('license_key', '').strip().upper()
        if not (dev_env and key == dev_env):
            host = '127.0.0.1'

    config = uvicorn.Config(application, host=host, port=port, forwarded_allow_ips='*')
    server = uvicorn.Server(config)
    application.state.server = server
    fastapi_app.state.server = server
    with open(PID_FILE, 'w') as fh:
        fh.write(str(os.getpid()))
    try:
        server.run()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
