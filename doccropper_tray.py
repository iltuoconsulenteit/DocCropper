import os
import platform
import subprocess
import logging
from pathlib import Path
import tempfile
import threading
import atexit
import webbrowser
from urllib.request import urlopen
import json
import time
from dotenv import load_dotenv

LANG = 'it'
TRANSLATIONS = {}

BASE_DIR = Path(__file__).resolve().parent
INSTALL_DIR = BASE_DIR / 'install'
SCRIPTS_DIR = BASE_DIR / 'scripts'

LOG_FILE = Path(tempfile.gettempdir()) / 'doccropper_tray.log'

# Store the tray process ID so launch scripts can detect it
TRAY_PID_FILE = Path(tempfile.gettempdir()) / 'doccropper_tray.pid'
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# Load environment variables from env/*.env files
ENV_DIR = BASE_DIR / 'env'
if ENV_DIR.is_dir():
    for env_file in ENV_DIR.glob('*.env'):
        load_dotenv(env_file, override=False)

def load_language():
    global LANG, TRANSLATIONS
    try:
        with open(BASE_DIR / 'settings.json') as fh:
            data = json.load(fh)
        LANG = data.get('language', 'it')
    except Exception:
        LANG = 'it'
    try:
        with open(BASE_DIR / 'static' / 'lang' / f'{LANG}.json') as fh:
            TRANSLATIONS = json.load(fh)
    except Exception:
        TRANSLATIONS = {}

def tr(key):
    return TRANSLATIONS.get(key, key)

load_language()

SYSTEM = platform.system()
START_SCRIPTS = {
    'Windows': 'start_DocCropper.bat',
    'Darwin': 'start_DocCropper.command',
}.get(SYSTEM, 'start_DocCropper.sh')
STOP_SCRIPTS = {
    'Windows': 'stop_DocCropper.bat',
    'Darwin': 'stop_DocCropper.command',
}.get(SYSTEM, 'stop_DocCropper.sh')
INSTALL_SCRIPTS = {
    'Windows': 'install_DocCropper.bat',
    'Darwin': 'install_DocCropper.command',
}.get(SYSTEM, 'install_DocCropper.sh')
UNINSTALL_SCRIPTS = {
    'Windows': 'uninstall_DocCropper.bat',
    'Darwin': 'uninstall_DocCropper.command',
}.get(SYSTEM, 'uninstall_DocCropper.sh')

ROLLBACK_SCRIPTS = {
    'Windows': 'rollback_DocCropper.bat',
    'Darwin': 'rollback_DocCropper.command',
}.get(SYSTEM, 'rollback_DocCropper.sh')

def is_developer():
    """Return True if a developer license is active."""
    settings_file = BASE_DIR / 'settings.json'
    try:
        with open(settings_file) as fh:
            data = json.load(fh)
        key = data.get('license_key', '').strip().upper()
        level = data.get('license_level', '').strip().lower()
        dev_env = os.environ.get('DOCROPPER_DEV_LICENSE', '').upper()
        masked = f"{key[:4]}..." if key else ""
        logging.info(
            "License check: level=%s key=%s env_dev=%s",
            level or "",
            masked,
            bool(dev_env),
        )
        return (
            level == 'developer'
            or (dev_env and key == dev_env)
            or key.endswith('-DEV')
        )
    except Exception:
        logging.exception("Unable to read settings for developer check")
        return False

def run_script(name, env=None, folder=INSTALL_DIR):
    """Run a helper script while logging output.

    The log file is opened only for the duration of the spawn so we don't keep
    the handle locked after starting the child process.
    """
    script = folder / name
    logging.info("Running %s", script)
    if SYSTEM == 'Windows':
        flags = 0
        if hasattr(subprocess, 'CREATE_NO_WINDOW'):
            flags = subprocess.CREATE_NO_WINDOW
        with open(LOG_FILE, 'a') as stdout:
            subprocess.Popen(['cmd', '/c', str(script)], env=env,
                             stdout=stdout, stderr=subprocess.STDOUT,
                             creationflags=flags)
    else:
        with open(LOG_FILE, 'a') as stdout:
            subprocess.Popen(['bash', str(script)], env=env,
                             stdout=stdout, stderr=subprocess.STDOUT)


def start_app():
    run_script(START_SCRIPTS, folder=SCRIPTS_DIR)

def stop_app():
    run_script(STOP_SCRIPTS, folder=SCRIPTS_DIR)

def update_main():
    env = os.environ.copy()
    env['BRANCH'] = 'main'
    run_script(INSTALL_SCRIPTS, env)

def update_branch():
    env = os.environ.copy()
    branch = env.get('DOCROPPER_BRANCH', 'main')
    env['BRANCH'] = branch
    run_script(INSTALL_SCRIPTS, env)

def uninstall_app():
    run_script(UNINSTALL_SCRIPTS)

def rollback_app():
    run_script(ROLLBACK_SCRIPTS, folder=SCRIPTS_DIR)

def open_browser():
    port = get_port()
    url = os.environ.get('DOCROPPER_OPEN_URL')
    if not url:
        url = f'http://127.0.0.1:{port}/'
    try:
        if not webbrowser.open(url):
            raise RuntimeError('webbrowser failed')
    except Exception:
        try:
            subprocess.Popen(['xdg-open', url])
        except Exception:
            logging.exception('Unable to open browser')

def get_port():
    try:
        with open(BASE_DIR / 'settings.json') as fh:
            data = json.load(fh)
        return int(data.get('port', 8765))
    except Exception:
        return 8765

def is_running():
    port = get_port()
    try:
        urlopen(f'http://127.0.0.1:{port}/', timeout=1)
        return True
    except Exception:
        return False

def quit_app(icon, item):
    icon.stop()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DocCropper tray helper")
    parser.add_argument("--no-tray", action="store_true",
                        help="Run without showing a system tray icon")
    parser.add_argument("--auto-start", action="store_true",
                        help="Start server immediately")
    args = parser.parse_args()

    developer = os.environ.get('DOCROPPER_DEVELOPER') == '1' or is_developer()
    logging.info("Tray icon started (developer=%s)", developer)
    try:
        TRAY_PID_FILE.write_text(str(os.getpid()))
    except Exception:
        pass
    atexit.register(lambda: TRAY_PID_FILE.unlink(missing_ok=True))

    running = is_running()

    if args.auto_start and not running:
        logging.info("Auto-start requested from start script")
        start_app()
        # give the server a moment to start
        time.sleep(1)
        running = is_running()

    if args.no_tray:
        logging.info("--no-tray specified, launching server directly")
        if not running:
            start_app()
        return

    if SYSTEM == 'Linux' and not os.environ.get('DISPLAY'):
        os.environ['DISPLAY'] = ':0'
        logging.info("DISPLAY not set; defaulting to :0")

    try:
        from pystray import Icon, Menu, MenuItem
        from PIL import Image, ImageDraw
    except Exception as e:
        logging.exception("Tray modules unavailable: %s", e)
        if not running:
            start_app()
        return

    BASE_IMAGE = None

    def load_base_image():
        nonlocal BASE_IMAGE
        for name in ('app_logo.png', 'header_logo.png'):
            path = BASE_DIR / 'static' / 'logos' / name
            if path.exists():
                BASE_IMAGE = Image.open(path).convert('RGBA').resize((64, 64))
                break
        else:
            BASE_IMAGE = Image.new('RGBA', (64, 64), 'white')

    def status_image(running):
        img = BASE_IMAGE.copy()
        draw = ImageDraw.Draw(img)
        color = 'green' if running else 'red'
        draw.ellipse((48, 48, 60, 60), fill=color)
        return img

    def create_image(running):
        return status_image(running)

    load_base_image()

    def update(state):
        icon.icon = create_image(state)

    def open_app(icon, item):
        open_browser()

    def start_action(icon, item):
        start_app()
        update(True)

    def stop_action(icon, item):
        stop_app()
        update(False)

    def update_main_action(icon, item):
        update_main()

    def uninstall_action(icon, item):
        uninstall_app()

    def rollback_action(icon, item):
        rollback_app()

    def update_branch_action(icon, item):
        update_branch()

    menu_items = [
        MenuItem(tr('openApp'), open_app, default=True),
        MenuItem(tr('startApp'), start_action),
        MenuItem(tr('stopApp'), stop_action),
        MenuItem(tr('updateMain'), update_main_action),
        MenuItem(tr('rollbackApp'), rollback_action),
        MenuItem(tr('uninstallApp'), uninstall_action)
    ]
    if developer:
        menu_items.append(MenuItem(tr('updateBranch'), update_branch_action))
    menu_items.append(MenuItem(tr('quit'), quit_app))

    icon = Icon(
        'DocCropper',
        create_image(running),
        'DocCropper',
        menu=Menu(*menu_items)
    )

    def setup(icon):
        icon.visible = True

    def poll():
        while True:
            state = is_running()
            icon.icon = create_image(state)
            time.sleep(5)

    thread = threading.Thread(target=poll, daemon=True)
    thread.start()

    try:
        icon.run(setup=setup)
    except Exception as e:
        logging.exception("Tray icon error: %s", e)
        logging.info("Falling back to running without tray")
        start_app()


if __name__ == '__main__':
    main()
