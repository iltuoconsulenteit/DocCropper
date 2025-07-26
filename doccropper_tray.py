import os
import platform
import subprocess
import logging
from pathlib import Path
import tempfile
from pystray import Icon, Menu, MenuItem
import threading
from PIL import Image, ImageDraw
import webbrowser
from urllib.request import urlopen
import json
import time
from dotenv import load_dotenv

LANG = 'en'
TRANSLATIONS = {}

BASE_DIR = Path(__file__).resolve().parent
INSTALL_DIR = BASE_DIR / 'install'
SCRIPTS_DIR = BASE_DIR / 'scripts'

LOG_FILE = Path(tempfile.gettempdir()) / 'doccropper_tray.log'
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
        LANG = data.get('language', 'en')
    except Exception:
        LANG = 'en'
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

def is_developer():
    settings_file = BASE_DIR / 'settings.json'
    try:
        with open(settings_file) as fh:
            data = json.load(fh)
        key = data.get('license_key', '').strip().upper()
        dev = os.environ.get('DOCROPPER_DEV_LICENSE', '').upper()
        return bool(dev) and key == dev
    except Exception:
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

def open_browser():
    port = get_port()
    webbrowser.open(f'http://127.0.0.1:{port}/')

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

BASE_IMAGE = None

def load_base_image():
    global BASE_IMAGE
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

def quit_app(icon, item):
    icon.stop()


def create_image(running):
    return status_image(running)


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

    load_base_image()
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

    def update(state):
        icon.icon = create_image(state)

    menu_items = [
        MenuItem(tr('openApp'), lambda icon, item: open_browser()),
        MenuItem(tr('startApp'), lambda icon, item: [start_app(), update(True)]),
        MenuItem(tr('stopApp'), lambda icon, item: [stop_app(), update(False)]),
        MenuItem(tr('updateMain'), lambda icon, item: update_main()),
        MenuItem(tr('uninstallApp'), lambda icon, item: uninstall_app())
    ]
    if developer:
        menu_items.append(MenuItem(tr('updateBranch'), lambda icon, item: update_branch()))
    menu_items.append(MenuItem(tr('quit'), quit_app))

    icon = Icon('DocCropper', create_image(running), 'DocCropper', menu=Menu(*menu_items))

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
