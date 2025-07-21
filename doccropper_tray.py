import os
import platform
import subprocess
import logging
from pathlib import Path
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import webbrowser
from urllib.request import urlopen
import json
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
INSTALL_DIR = BASE_DIR / 'install'
SCRIPTS_DIR = BASE_DIR / 'scripts'

LOG_FILE = BASE_DIR / 'doccropper_tray.log'
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

def is_developer():
    settings_file = BASE_DIR / 'settings.json'
    try:
        with open(settings_file) as fh:
            data = json.load(fh)
        key = data.get('license_key', '').strip().upper()
        dev = os.environ.get('DOCROPPER_DEV_LICENSE', 'ILTUOCONSULENTEIT-DEV').upper()
        return key == dev
    except Exception:
        return False

def run_script(name, env=None, folder=INSTALL_DIR):
    script = folder / name
    logging.info("Running %s", script)
    stdout = open(LOG_FILE, 'a')
    if SYSTEM == 'Windows':
        flags = 0
        if hasattr(subprocess, 'CREATE_NO_WINDOW'):
            flags = subprocess.CREATE_NO_WINDOW
        subprocess.Popen(['cmd', '/c', str(script)], env=env,
                         stdout=stdout, stderr=subprocess.STDOUT,
                         creationflags=flags)
    else:
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

def open_browser():
    port = get_port()
    webbrowser.open(f'http://127.0.0.1:{port}/')

def get_port():
    try:
        with open(BASE_DIR / 'settings.json') as fh:
            data = json.load(fh)
        return int(data.get('port', 8000))
    except Exception:
        return 8000

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
    path = BASE_DIR / 'static' / 'logos' / 'header_logo.png'
    if path.exists():
        BASE_IMAGE = Image.open(path).convert('RGBA').resize((64, 64))
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
        start_app()
        running = True

    if args.no_tray:
        logging.info("--no-tray specified, launching server directly")
        if not running:
            start_app()
        return

    def update(state):
        icon.icon = create_image(state)

    menu_items = [
        MenuItem('Open DocCropper', lambda icon, item: open_browser()),
        MenuItem('Start DocCropper', lambda icon, item: [start_app(), update(True)]),
        MenuItem('Stop DocCropper', lambda icon, item: [stop_app(), update(False)]),
        MenuItem('Update from main', lambda icon, item: update_main())
    ]
    if developer:
        menu_items.append(MenuItem('Update from branch', lambda icon, item: update_branch()))
    menu_items.append(MenuItem('Quit', quit_app))

    icon = Icon('DocCropper', create_image(running), 'DocCropper', menu=Menu(*menu_items))

    try:
        icon.run()
    except Exception as e:
        logging.exception("Tray icon error: %s", e)
        logging.info("Falling back to running without tray")
        start_app()


if __name__ == '__main__':
    main()
