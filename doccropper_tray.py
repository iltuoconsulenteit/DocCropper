import os
import platform
import subprocess
import logging
from pathlib import Path
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import json
from dotenv import load_dotenv
import signal

BASE_DIR = Path(__file__).resolve().parent
INSTALL_DIR = BASE_DIR / 'install'
SCRIPTS_DIR = BASE_DIR / 'scripts'
PID_FILE = BASE_DIR / 'doccropper.pid'

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

app_running = False

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


def is_app_running():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except Exception:
            PID_FILE.unlink(missing_ok=True)
    return False


def refresh_menu(icon):
    running = is_app_running()
    start_item.enabled = not running
    stop_item.enabled = running
    start_item.icon = RED_DOT if not running else GREEN_DOT
    stop_item.icon = GREEN_DOT if running else RED_DOT
    icon.update_menu()


def start_app(icon=None):
    run_script(START_SCRIPTS, folder=SCRIPTS_DIR)
    if icon:
        refresh_menu(icon)

def stop_app(icon=None):
    run_script(STOP_SCRIPTS, folder=SCRIPTS_DIR)
    if icon:
        refresh_menu(icon)

def update_main():
    env = os.environ.copy()
    env['BRANCH'] = 'main'
    run_script(INSTALL_SCRIPTS, env)

def update_branch():
    env = os.environ.copy()
    branch = env.get('DOCROPPER_BRANCH', 'main')
    env['BRANCH'] = branch
    run_script(INSTALL_SCRIPTS, env)

def quit_app(icon, item):
    icon.stop()


def create_fallback_image():
    image = Image.new('RGB', (64, 64), 'white')
    draw = ImageDraw.Draw(image)
    draw.rectangle((8, 8, 56, 56), fill='black')
    draw.text((16, 20), 'DC', fill='white')
    return image


def load_tray_icon():
    logo = BASE_DIR / 'static' / 'logos' / 'header_logo.png'
    try:
        return Image.open(logo)
    except Exception:
        return create_fallback_image()


def make_dot(color):
    img = Image.new('RGB', (16, 16), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((3, 3, 13, 13), fill=color)
    return img


GREEN_DOT = make_dot('green')
RED_DOT = make_dot('red')


def main():
    import argparse

    parser = argparse.ArgumentParser(description="DocCropper tray helper")
    parser.add_argument("--no-tray", action="store_true",
                        help="Run without showing a system tray icon")
    parser.add_argument("--auto-start", action="store_true",
                        help="Start the server immediately")
    args = parser.parse_args()

    developer = os.environ.get('DOCROPPER_DEVELOPER') == '1' or is_developer()
    logging.info("Tray icon started (developer=%s)", developer)

    if args.no_tray:
        logging.info("--no-tray specified, launching server directly")
        start_app()
        return

    if args.auto_start:
        logging.info("--auto-start specified, starting server")
        start_app()

    global start_item, stop_item
    start_item = MenuItem('Start DocCropper', lambda icon, item: start_app(icon))
    stop_item = MenuItem('Stop DocCropper', lambda icon, item: stop_app(icon))
    menu_items = [
        start_item,
        stop_item,
        MenuItem('Update from main', lambda icon, item: update_main())
    ]
    if developer:
        menu_items.append(MenuItem('Update from branch', lambda icon, item: update_branch()))
    menu_items.append(MenuItem('Quit', quit_app))

    icon = Icon('DocCropper', load_tray_icon(), 'DocCropper', menu=Menu(*menu_items))
    refresh_menu(icon)
    try:
        icon.run()
    except Exception as e:
        logging.exception("Tray icon error: %s", e)
        logging.info("Falling back to running without tray")
        start_app()


if __name__ == '__main__':
    main()
