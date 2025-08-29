import argparse
import os
import signal
import tempfile

import uvicorn

from platform.config.asgi import application
from services.api.app import app as fastapi_app, load_settings, DEV_LICENSE_KEY_UPPER

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
