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

# Load environment variables from env/*.env files, allowing them to
# override any preexisting environment variables so that license
# information from the local files always takes precedence.
ENV_DIR = BASE_DIR / 'env'
if ENV_DIR.is_dir():
    for env_file in ENV_DIR.glob('*.env'):
        load_dotenv(env_file, override=True)

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
try:
    VERSION = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=BASE_DIR,
        stderr=subprocess.DEVNULL,
    ).decode().strip()
    VERSION_DATE = subprocess.check_output(
        ["git", "log", "-1", "--format=%cd", "--date=short"],
        cwd=BASE_DIR,
        stderr=subprocess.DEVNULL,
    ).decode().strip()
except Exception:
    # Fall back to optional environment variables when running without a
    # Git repository available (e.g. packaged installations)
    VERSION = os.getenv("DOCROPPER_BUILD_VERSION", "unknown")
    VERSION_DATE = os.getenv("DOCROPPER_BUILD_DATE", "")


def get_license_info():
    """Return license level, key, masked key, dev flag and license name."""
    settings_file = BASE_DIR / 'settings.json'
    try:
        with open(settings_file) as fh:
            data = json.load(fh)
    except Exception:
        data = {}

    key = data.get('license_key', '').strip().upper()
    level = data.get('license_level', '').strip().lower()
    name = data.get('license_name', '').strip()

    env_key = os.environ.get('DOCROPPER_LICENSE_KEY', '').strip().upper()
    env_level = os.environ.get('DOCROPPER_LICENSE_LEVEL', '').strip().lower()
    env_name = os.environ.get('DOCROPPER_LICENSE_NAME', '').strip()
    if env_key:
        key = env_key
    if env_level:
        level = env_level
    if env_name:
        name = env_name

    dev_env = os.environ.get('DOCROPPER_DEV_LICENSE', '').strip().upper()
    if dev_env and not key:
        key = dev_env
    if dev_env and level != 'developer':
        level = 'developer'
    if not name and (dev_env or key.endswith('-DEV')):
        name = 'Developer'
    masked = f"{key[:4]}..." if key else ""
    return level, key, masked, bool(dev_env), name


def is_developer():
    """Return True if a developer license is active."""
    level, key, masked, dev_env, _ = get_license_info()
    logging.info(
        "License check: level=%s key=%s env_dev=%s version=%s date=%s",
        level or "",
        masked,
        dev_env,
        VERSION,
        VERSION_DATE,
    )
    return (
        level == 'developer' or key.endswith('-DEV') or dev_env
    )

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


def fetch_server_build_info():
    port = get_port()
    try:
        with urlopen(f'http://127.0.0.1:{port}/settings/?_={int(time.time())}', timeout=2) as resp:
            data = json.load(resp)
        return (
            data.get('version'),
            data.get('version_date'),
            data.get('license_level'),
            data.get('license_key'),
            data.get('license_name'),
        )
    except Exception:
        return None, None, None, None, None

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
    global VERSION, VERSION_DATE
    parser = argparse.ArgumentParser(description="DocCropper tray helper")
    parser.add_argument("--no-tray", action="store_true",
                        help="Run without showing a system tray icon")
    parser.add_argument("--auto-start", action="store_true",
                        help="Start server immediately")
    args = parser.parse_args()

    force_dev = os.environ.get('DOCROPPER_DEVELOPER') == '1'
    level, key, masked, _, name = get_license_info()
    developer = force_dev or is_developer()
    srv_v, srv_d, srv_level, srv_key, srv_name = fetch_server_build_info()
    if srv_v:
        VERSION = srv_v
    if srv_d:
        VERSION_DATE = srv_d
    if srv_level:
        level = srv_level
    if srv_key:
        key = srv_key
        masked = f"{key[:4]}..."
    if srv_name:
        name = srv_name
    logging.info(
        "Tray icon started (developer=%s license=%s name=%s key=%s version=%s date=%s)",
        developer,
        level or "",
        name or "",
        masked,
        VERSION,
        VERSION_DATE,
    )
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
        refresh_from_server()

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

    info_item = MenuItem(
        f"v{VERSION} ({VERSION_DATE}) - {level or ''} {name or ''} {masked}".strip(),
        None,
        enabled=False,
    )
    menu_items = [
        info_item,
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

    title = f"DocCropper {VERSION} ({VERSION_DATE}) - {level or ''} {name or ''} {masked}".strip()
    icon = Icon(
        'DocCropper',
        create_image(running),
        title,
        menu=Menu(*menu_items)
    )

    def refresh_from_server():
        global VERSION, VERSION_DATE
        nonlocal level, key, masked, name
        v, d, lvl, k, n = fetch_server_build_info()
        updated = False
        if v:
            VERSION = v
            updated = True
        if d:
            VERSION_DATE = d
            updated = True
        if lvl:
            level = lvl
            updated = True
        if k:
            key = k
            masked = f"{k[:4]}..."
            updated = True
        if n:
            name = n
            updated = True
        if updated:
            info_item.text = f"v{VERSION} ({VERSION_DATE}) - {level or ''} {name or ''} {masked}".strip()
            icon.title = f"DocCropper {VERSION} ({VERSION_DATE}) - {level or ''} {name or ''} {masked}".strip()

    if running:
        refresh_from_server()

    def setup(icon):
        icon.visible = True

    def poll():
        while True:
            state = is_running()
            icon.icon = create_image(state)
            if state:
                refresh_from_server()
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
