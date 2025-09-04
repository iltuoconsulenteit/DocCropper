import base64
import io
import logging
import json
import math
import os
import shutil
import time
import uuid
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, Body, Request, Depends, HTTPException
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


class NoCacheStaticFiles(StaticFiles):
    """StaticFiles that sets no-cache headers to avoid proxy caching."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            # Prevent browsers from reusing cached assets so version updates
            # are reflected immediately on refresh
            response.headers["Cache-Control"] = "no-store, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            # Allow help pages like the wiki to be embedded in the UI
            response.headers.pop("X-Frame-Options", None)
            response.headers["Content-Security-Policy"] = "frame-ancestors *"
        return response
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet
import subprocess
import sys
import tempfile
from dotenv import load_dotenv
import urllib.request
import urllib.parse
import socket
from pathlib import Path
import importlib
import importlib.util
from types import SimpleNamespace

import bcrypt as _bcrypt
if not hasattr(_bcrypt, "__about__"):
    _bcrypt.__about__ = SimpleNamespace(__version__=getattr(_bcrypt, "__version__", ""))

from passlib.hash import bcrypt

_cv2 = None
_np = None
_fitz = None

# Ensure the standard library 'platform' module is used even though a local
# Django package named 'platform' exists in the project root.
_platform_spec = importlib.util.spec_from_file_location(
    "platform", Path(os.__file__).resolve().parent / "platform.py"
)
platform = importlib.util.module_from_spec(_platform_spec)
_platform_spec.loader.exec_module(platform)

def get_cv2():
    global _cv2
    if _cv2 is None:
        _cv2 = importlib.import_module("cv2")
    return _cv2

def get_np():
    global _np
    if _np is None:
        _np = importlib.import_module("numpy")
    return _np

def get_fitz():
    global _fitz
    if _fitz is None:
        _fitz = importlib.import_module("fitz")
    return _fitz
from plugin.core.sign import register as register_sign
from app.licensing.check import verify_license
from jose import jwt, JWTError
import time
from app.auth.routes import router as auth_router, fastapi_users
from app.auth.models import User
from plugin.core.mobilesign import register as register_mobilesign
from plugin.core.remotesign import register as register_remotesign
from plugin.core.docuseal import register as register_docuseal
from plugin.core.crop import register as register_crop
from plugin.core.removebg import register as register_removebg
from plugin.core.compresspdf import register as register_compresspdf
from plugin.core.watermark import register as register_watermark
from plugin.core.login import register as register_login
from plugin.core.downloadpng import register as register_downloadpng
from plugin.core.pageselect import register as register_pageselect
from plugin.core.colormode import register as register_colormode
from plugin.core.scan import register as register_scan
from plugin.core.cloudsave import register as register_cloudsave

try:
    import stripe
except Exception:
    stripe = None

try:
    from pyhanko.sign import signers
except Exception:
    signers = None

try:
    import pytesseract
except Exception:
    pytesseract = None


BASE_DIR = Path(__file__).resolve().parents[2]
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
# Additional file storing values enforced by a license check
LICENSE_OVERRIDES_FILE = os.path.join(BASE_DIR, "license_overrides.json")
# Load environment variables from any .env files in env/
ENV_DIR = os.path.join(BASE_DIR, "env")


def load_env_files(override: bool = False) -> None:
    """Load all .env files so license changes take effect without restart."""
    if os.path.isdir(ENV_DIR):
        for name in os.listdir(ENV_DIR):
            if name.endswith(".env"):
                load_dotenv(os.path.join(ENV_DIR, name), override=override)


# Initial environment load
load_env_files()

# Directory containing per-user settings
USERS_DIR = os.path.join(BASE_DIR, "users")

DEFAULT_DEV_PASSWORD = os.getenv("DOCROPPER_DEV_PASSWORD", "87654321")
DEFAULT_SETTINGS_PASSWORD = os.getenv("DOCROPPER_SETTINGS_PASSWORD", "12345678")

# Read/write values that the license server enforces. They override normal
# settings and cannot be changed by users.
def load_license_overrides() -> dict:
    if not os.path.exists(LICENSE_OVERRIDES_FILE):
        return {}
    try:
        with open(LICENSE_OVERRIDES_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}

def save_license_overrides(update: dict) -> dict:
    data = load_license_overrides()
    data.update(update)
    with open(LICENSE_OVERRIDES_FILE, "w") as fh:
        json.dump(data, fh)
    return data

# Developer license key for demonstration (case-insensitive)
DEV_LICENSE_KEY = os.environ.get("DOCROPPER_DEV_LICENSE", "DEVELOPER")
DEV_LICENSE_KEY_UPPER = DEV_LICENSE_KEY.upper()
MANUAL_LICENSE_KEY = os.environ.get("DOCROPPER_MANUAL_LICENSE", "").upper()
ONLINE_LICENSE_KEY = os.environ.get("DOCROPPER_ONLINE_LICENSE", "").upper()
DEMO_FULL_LICENSE_KEY = "DEMO-FULL-DC"
LICENSE_SECRET = os.environ.get("LICENSE_SECRET", "change-me")
DEFAULT_SPONSOR_FRAME = (
    "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2F"
    "iltuoconsulenteit%3Flocale%3Dit_IT&tabs=timeline&width=340&height=500&small_header=true&"
    "adapt_container_width=true&hide_cover=true&show_facepile=false"
)

def get_version_info() -> tuple[str, str]:
    """Return the current Git commit hash and date."""
    try:
        version = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=BASE_DIR,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cd", "--date=short"],
            cwd=BASE_DIR,
            stderr=subprocess.DEVNULL,
        ).decode().strip()
    except Exception:
        version = "unknown"
        date = ""
    return version, date

def get_cache_bust() -> str:
    version, _ = get_version_info()
    return f"?v={version}" if version != "unknown" else ""

VERSION, VERSION_DATE = get_version_info()
CACHE_BUST = get_cache_bust()

SESSIONS_ROOT = "sessions"
SIGNATURES_DIR = "signatures"
PID_FILE = os.path.join(tempfile.gettempdir(), "doccropper.pid")
ENC_SUFFIX = ".enc"
SESSION_KEYS: dict[str, bytes] = {}
DEFAULT_MAX_UPLOAD_MB = 5
MAX_UPLOAD_MB = int(os.getenv("DOCROPPER_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB)))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

def repo_has_updates() -> bool:
    """Check if remote Git repository has new commits."""
    try:
        subprocess.run(
            ["git", "fetch"],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5,
        )
        local = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=BASE_DIR, timeout=5
        ).strip()
        remote = subprocess.check_output(
            ["git", "rev-parse", "@{u}"], cwd=BASE_DIR, timeout=5
        ).strip()
        return local != remote
    except Exception:
        return False

def run_update_script():
    env = os.environ.copy()
    env.setdefault("BRANCH", "main")
    script = BASE_DIR / "install" / "install_DocCropper.sh"
    subprocess.Popen(["bash", str(script)], cwd=BASE_DIR, env=env)

def run_rollback_script():
    system = platform.system()
    script = {
        "Windows": BASE_DIR / "scripts" / "rollback_DocCropper.bat",
        "Darwin": BASE_DIR / "scripts" / "rollback_DocCropper.command",
    }.get(system, BASE_DIR / "scripts" / "rollback_DocCropper.sh")
    if system == "Windows":
        subprocess.Popen(["cmd", "/c", str(script)], cwd=BASE_DIR)
    else:
        subprocess.Popen(["bash", str(script)], cwd=BASE_DIR)

DEFAULT_SETTINGS = {
    "language": "it",
    "layout": 1,
    "orientation": "portrait",
    "arrangement": "auto",
    "scale_mode": "fit",
    "scale_percent": 100,
    "brightness": 100,
    "contrast": 100,
    "port": 8765,
    "license_key": "",
    "license_name": "",
    "license_token": "",
    "payment_mode": "donation",
    "paypal_link": "",
    "stripe_link": "",
    "stripe_secret_key": "",
    "stripe_publishable_key": "",
    "stripe_price_pro": "",
    "stripe_price_full": "",
    "stripe_success_url": "",
    "stripe_cancel_url": "",
    "bank_info": "",
    "google_client_id": "",
    "license_check": False,
    "license_level": "free",
    "brand_html": "",
    "client_logo": "client_logo.png",
    "sponsor_logo": "sponsor_logo.png",
    "client_url": "",
    "sponsor_url": "",
    "sponsor_banner": "",
    "sponsor_frame": "",
    "sponsor_plugin": "",
    "sponsor_facebook_page": "iltuoconsulenteit",
    "sponsor_instagram_profile": "",
    "sponsor_slides": [],
    "sponsor_frame_width": 340,
    "sponsor_frame_height": 500,
    "sponsor_thumb_width": 150,
    "sponsor_thumb_height": 150,
    "sponsor_scale": 100,
    "sponsor_bottom": 80,
    "brand_height": 80,
    "brand_gap": 20,
    "blank_threshold": 95,
    "skip_blank": True,
    "max_upload_files": 10,
    "max_upload_mb": 5,
    "enable_sponsor_video": False,
    "banner_images": ["DocCropper_slogan_main_{{lang}}.png"],
    "developer_watermark": False,
    "demo_full_mode": False,
    "public_url": "",
    "template": "static",
    "update_pin": "",
    "update_interval": 3600000,
    "developer_password_hash": bcrypt.hash(DEFAULT_DEV_PASSWORD),
}

def verify_license_server(key: str) -> bool:
    url = os.getenv("LICENSE_SERVER", "https://license.doccropper.it/verify")
    try:
        with urllib.request.urlopen(f"{url}?key={urllib.parse.quote(key)}") as resp:
            data = json.loads(resp.read().decode())
            return bool(data.get("valid"))
    except Exception:
        logger.exception("License check failed")
        return False

def get_session_dir(session_id: str) -> str:
    if not session_id:
        return None
    path = os.path.join(SESSIONS_ROOT, session_id)
    os.makedirs(path, exist_ok=True)
    if session_id not in SESSION_KEYS:
        SESSION_KEYS[session_id] = Fernet.generate_key()
    return path

def cleanup_old_sessions(max_age: int = 600):
    if not os.path.exists(SESSIONS_ROOT):
        return
    now = time.time()
    for name in os.listdir(SESSIONS_ROOT):
        p = os.path.join(SESSIONS_ROOT, name)
        try:
            if os.path.isdir(p) and now - os.path.getmtime(p) > max_age:
                shutil.rmtree(p, ignore_errors=True)
                SESSION_KEYS.pop(name, None)
        except Exception:
            pass

def encrypt_bytes(session_id: str, data: bytes) -> bytes:
    key = SESSION_KEYS.get(session_id)
    if not key:
        key = Fernet.generate_key()
        SESSION_KEYS[session_id] = key
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_file(session_id: str, path: str) -> bytes | None:
    if not os.path.exists(path):
        return None
    key = SESSION_KEYS.get(session_id)
    if not key:
        return None
    try:
        with open(path, 'rb') as fh:
            enc = fh.read()
        return Fernet(key).decrypt(enc)
    except Exception:
        return None

def get_lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def load_settings():
    # Reload environment variables so license changes are picked up on each call
    load_env_files(override=True)
    global DEV_LICENSE_KEY, DEV_LICENSE_KEY_UPPER, MANUAL_LICENSE_KEY, ONLINE_LICENSE_KEY
    DEV_LICENSE_KEY = os.environ.get("DOCROPPER_DEV_LICENSE", "DEVELOPER")
    DEV_LICENSE_KEY_UPPER = DEV_LICENSE_KEY.upper().strip()
    MANUAL_LICENSE_KEY = os.environ.get("DOCROPPER_MANUAL_LICENSE", "").upper().strip()
    ONLINE_LICENSE_KEY = os.environ.get("DOCROPPER_ONLINE_LICENSE", "").upper().strip()
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as fh:
            json.dump(DEFAULT_SETTINGS, fh)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE) as fh:
            base = json.load(fh)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(base)
        plugins_dir = os.path.join(BASE_DIR, "plugin", "core")
        try:
            for name in os.listdir(plugins_dir):
                cfg_path = os.path.join(plugins_dir, name, "settings.json")
                if os.path.exists(cfg_path):
                    with open(cfg_path) as pf:
                        merged.update(json.load(pf))
        except Exception:
            pass
        max_mb_env = os.getenv("DOCROPPER_MAX_UPLOAD_MB")
        if max_mb_env:
            merged["max_upload_mb"] = int(max_mb_env)
        env_key = os.getenv("DOCROPPER_LICENSE_KEY")
        env_name = os.getenv("DOCROPPER_LICENSE_NAME")
        env_token = os.getenv("DOCROPPER_LICENSE_TOKEN")
        google_id = os.getenv("DOCROPPER_GOOGLE_CLIENT_ID")
        env_check = os.getenv("LICENSE_CHECK")
        env_level = os.getenv("DOCROPPER_LICENSE_LEVEL")
        dev_wm_env = os.getenv("DOCROPPER_DEV_WATERMARK")
        stripe_secret = os.getenv("STRIPE_SECRET_KEY")
        stripe_publish = os.getenv("STRIPE_PUBLISHABLE_KEY")
        stripe_pro = os.getenv("STRIPE_PRICE_PRO")
        stripe_full = os.getenv("STRIPE_PRICE_FULL")
        stripe_success = os.getenv("STRIPE_SUCCESS_URL")
        stripe_cancel = os.getenv("STRIPE_CANCEL_URL")
        public_url_env = os.getenv("DOCROPPER_PUBLIC_URL")
        lan_limit_env = os.getenv("DOCROPPER_LAN_USER_LIMIT")
        global MAX_UPLOAD_MB, MAX_UPLOAD_BYTES
        MAX_UPLOAD_MB = int(merged.get("max_upload_mb", DEFAULT_MAX_UPLOAD_MB))
        MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024
        if env_key:
            merged["license_key"] = env_key
        if env_name:
            merged["license_name"] = env_name
        if env_token:
            merged["license_token"] = env_token
        if google_id:
            merged["google_client_id"] = google_id
        if env_check is not None:
            merged["license_check"] = env_check.lower() == "true"
        if env_level:
            merged["license_level"] = env_level.lower()
        if dev_wm_env is not None:
            merged["developer_watermark"] = dev_wm_env.lower() == "true"
        enable_remotesign_env = os.getenv("DOCROPPER_ENABLE_REMOTESIGN")
        if enable_remotesign_env is not None:
            merged["enable_remotesign"] = enable_remotesign_env.lower() == "true"
        remotesign_dev_env = os.getenv("DOCROPPER_REMOTESIGN_DEV_ONLY")
        if remotesign_dev_env is not None:
            merged["remotesign_dev_only"] = remotesign_dev_env.lower() == "true"
        docuseal_url = os.getenv("DOCUSEAL_API_URL")
        if docuseal_url:
            merged["docuseal_api_url"] = docuseal_url
        docuseal_key = os.getenv("DOCUSEAL_API_KEY")
        if docuseal_key:
            merged["docuseal_api_key"] = docuseal_key
        enable_docuseal_env = os.getenv("DOCROPPER_ENABLE_DOCUSEAL")
        if enable_docuseal_env is not None:
            merged["enable_docuseal"] = enable_docuseal_env.lower() == "true"
        docuseal_dev_env = os.getenv("DOCROPPER_DOCUSEAL_DEV_ONLY")
        if docuseal_dev_env is not None:
            merged["docuseal_dev_only"] = docuseal_dev_env.lower() == "true"
        enable_watermark_env = os.getenv("DOCROPPER_ENABLE_WATERMARK")
        if enable_watermark_env is not None:
            merged["enable_watermark"] = enable_watermark_env.lower() == "true"
        watermark_dev_env = os.getenv("DOCROPPER_WATERMARK_DEV_ONLY")
        if watermark_dev_env is not None:
            merged["watermark_dev_only"] = watermark_dev_env.lower() == "true"
        enable_downloadpng_env = os.getenv("DOCROPPER_ENABLE_DOWNLOADPNG")
        if enable_downloadpng_env is not None:
            merged["enable_downloadpng"] = enable_downloadpng_env.lower() == "true"
        downloadpng_dev_env = os.getenv("DOCROPPER_DOWNLOADPNG_DEV_ONLY")
        if downloadpng_dev_env is not None:
            merged["downloadpng_dev_only"] = downloadpng_dev_env.lower() == "true"
        enable_pageselect_env = os.getenv("DOCROPPER_ENABLE_PAGESELECT")
        if enable_pageselect_env is not None:
            merged["enable_pageselect"] = enable_pageselect_env.lower() == "true"
        pageselect_dev_env = os.getenv("DOCROPPER_PAGESELECT_DEV_ONLY")
        if pageselect_dev_env is not None:
            merged["pageselect_dev_only"] = pageselect_dev_env.lower() == "true"
        enable_colormode_env = os.getenv("DOCROPPER_ENABLE_COLORMODE")
        if enable_colormode_env is not None:
            merged["enable_colormode"] = enable_colormode_env.lower() == "true"
        colormode_dev_env = os.getenv("DOCROPPER_COLORMODE_DEV_ONLY")
        if colormode_dev_env is not None:
            merged["colormode_dev_only"] = colormode_dev_env.lower() == "true"
        enable_imageeditor_env = os.getenv("DOCROPPER_ENABLE_IMAGEEDITOR")
        if enable_imageeditor_env is not None:
            merged["enable_imageeditor"] = enable_imageeditor_env.lower() == "true"
        imageeditor_dev_env = os.getenv("DOCROPPER_IMAGEEDITOR_DEV_ONLY")
        if imageeditor_dev_env is not None:
            merged["imageeditor_dev_only"] = imageeditor_dev_env.lower() == "true"
        if stripe_secret:
            merged["stripe_secret_key"] = stripe_secret
        if stripe_publish:
            merged["stripe_publishable_key"] = stripe_publish
        if stripe_pro:
            merged["stripe_price_pro"] = stripe_pro
        if stripe_full:
            merged["stripe_price_full"] = stripe_full
        if stripe_success:
            merged["stripe_success_url"] = stripe_success
        if stripe_cancel:
            merged["stripe_cancel_url"] = stripe_cancel
        if public_url_env:
            merged["public_url"] = public_url_env
        if lan_limit_env:
            try:
                merged["lan_user_limit"] = int(lan_limit_env)
            except ValueError:
                pass
        sponsor_plugin_env = os.getenv("SPONSOR_PLUGIN")
        if sponsor_plugin_env is not None:
            merged["sponsor_plugin"] = sponsor_plugin_env
        fb_page_env = os.getenv("SPONSOR_FACEBOOK_PAGE")
        if fb_page_env:
            merged["sponsor_facebook_page"] = fb_page_env
        insta_env = os.getenv("SPONSOR_INSTAGRAM_PROFILE")
        if insta_env:
            merged["sponsor_instagram_profile"] = insta_env
        slides_env = os.getenv("SPONSOR_SLIDES")
        if slides_env:
            merged["sponsor_slides"] = [s.strip() for s in slides_env.split(",") if s.strip()]

        if "developer_password_hash" not in merged:
            merged["developer_password_hash"] = bcrypt.hash(DEFAULT_DEV_PASSWORD)
        if "settings_password_hash" not in merged:
            merged["settings_password_hash"] = bcrypt.hash(DEFAULT_SETTINGS_PASSWORD)
        token = merged.get("license_token")
        if token:
            try:
                payload = jwt.decode(token, LICENSE_SECRET, algorithms=["HS256"])
                exp = payload.get("expires_at")
                now = int(time.time())
                if exp and exp < now:
                    merged["license_level"] = "free"
                else:
                    merged["license_type"] = payload.get("license_type", "manual")
                    merged["license_name"] = payload.get("license_name", merged.get("license_name", ""))
                    merged["license_level"] = "full"
                    merged["license_key"] = token
            except JWTError:
                merged["license_level"] = "free"

        # Apply values enforced by a previous license check
        overrides = load_license_overrides()
        if overrides:
            merged.update(overrides)

        dev_env = DEV_LICENSE_KEY_UPPER
        manual_env = MANUAL_LICENSE_KEY
        online_env = ONLINE_LICENSE_KEY
        key_upper = merged.get("license_key", "").strip().upper()
        is_demo = key_upper == DEMO_FULL_LICENSE_KEY
        is_dev = (dev_env and key_upper == dev_env) or key_upper.endswith("-DEV")
        if is_demo:
            merged["license_level"] = "full"
            merged["license_type"] = "demo"
            merged["demo_full_mode"] = True
            if not merged.get("license_name"):
                merged["license_name"] = "Demo User"
            merged["enable_mobilesign"] = True
            if not merged.get("paypal_link"):
                merged["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
            if not merged.get("public_url"):
                merged["public_url"] = "https://doccropper.iltuoconsulenteit.it"
        elif is_dev:
            merged["license_level"] = "full"
            merged["license_type"] = "developer"
            if not merged.get("license_name"):
                merged["license_name"] = "Developer"
            merged["enable_mobilesign"] = True
        elif manual_env and key_upper == manual_env:
            merged["license_level"] = "full"
            merged["license_type"] = "manual"
            if not merged.get("license_name"):
                merged["license_name"] = "Manual License"
        elif online_env and key_upper == online_env:
            merged["license_level"] = "full"
            merged["license_type"] = "online"
            merged["license_check"] = True
            if not merged.get("license_name"):
                merged["license_name"] = "Online License"
        else:
            merged["license_level"] = "full"
            merged["license_type"] = "demo"
            merged["demo_full_mode"] = True
            if not merged.get("license_name"):
                merged["license_name"] = "Demo User"
            merged["enable_mobilesign"] = True
            if not merged.get("paypal_link"):
                merged["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
            if not merged.get("public_url"):
                merged["public_url"] = "https://doccropper.iltuoconsulenteit.it"
            is_demo = True
        if (is_demo or is_dev) and not merged.get("sponsor_frame"):
            merged["sponsor_frame"] = DEFAULT_SPONSOR_FRAME
        try:
            from plugin.core import sponsorframe
            sponsor_dev = str(
                os.getenv(
                    "DOCROPPER_SPONSORFRAME_DEV_ONLY",
                    merged.get("sponsorframe_dev_only", False),
                )
            ).lower() == "true"
            if not sponsor_dev or is_dev:
                merged.update(sponsorframe.get_config(merged))
        except Exception:
            logger.exception("sponsor plugin failed")
        logger.info(
            "License key '%s' loaded (level: %s)",
            merged.get("license_key", ""),
            merged.get("license_level", ""),
        )
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

# Initialize global upload limits from settings
load_settings()

def save_settings(update: dict):
    data = load_settings()
    overrides = load_license_overrides()
    filtered = {k: v for k, v in update.items() if k not in overrides}
    plugin_fields = {
        'docuseal': ['enable_docuseal', 'docuseal_dev_only', 'docuseal_api_url', 'docuseal_api_key'],
        'remotesign': ['enable_remotesign', 'remotesign_dev_only'],
        'downloadpng': ['enable_downloadpng', 'downloadpng_dev_only'],
        'pageselect': ['enable_pageselect', 'pageselect_dev_only'],
        'colormode': ['enable_colormode', 'colormode_dev_only'],
        'watermark': ['enable_watermark', 'watermark_dev_only'],
        'imageeditor': ['enable_imageeditor', 'imageeditor_dev_only'],
        'scan': ['enable_scan', 'scan_dev_only']
    }
    plugin_updates = {}
    for pname, keys in plugin_fields.items():
        subset = {k: filtered.pop(k) for k in list(filtered.keys()) if k in keys}
        if subset:
            plugin_updates[pname] = subset
    data.update(filtered)
    if os.getenv("DOCROPPER_PUBLIC_URL"):
        data["public_url"] = os.getenv("DOCROPPER_PUBLIC_URL")
    key_upper = data.get("license_key", "").strip().upper()
    dev_env = DEV_LICENSE_KEY_UPPER
    manual_env = MANUAL_LICENSE_KEY
    online_env = ONLINE_LICENSE_KEY
    if key_upper == DEMO_FULL_LICENSE_KEY:
        data["license_level"] = "full"
        data["license_type"] = "demo"
        data["demo_full_mode"] = True
        if not data.get("license_name"):
            data["license_name"] = "Demo User"
        data["enable_mobilesign"] = True
        if not data.get("paypal_link"):
            data["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
        if not data.get("public_url"):
            data["public_url"] = "https://doccropper.iltuoconsulenteit.it"
    elif (dev_env and key_upper == dev_env) or key_upper.endswith("-DEV"):
        data["license_level"] = "full"
        data["license_type"] = "developer"
        if not data.get("license_name"):
            data["license_name"] = "Developer"
        data["enable_mobilesign"] = True
    elif manual_env and key_upper == manual_env:
        data["license_level"] = "full"
        data["license_type"] = "manual"
        if not data.get("license_name"):
            data["license_name"] = "Manual License"
    elif online_env and key_upper == online_env:
        data["license_level"] = "full"
        data["license_type"] = "online"
        data["license_check"] = True
        if not data.get("license_name"):
            data["license_name"] = "Online License"
    else:
        data["license_level"] = "full"
        data["license_type"] = "demo"
        data["demo_full_mode"] = True
        if not data.get("license_name"):
            data["license_name"] = "Demo User"
        data["enable_mobilesign"] = True
        if not data.get("paypal_link"):
            data["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
        if not data.get("public_url"):
            data["public_url"] = "https://doccropper.iltuoconsulenteit.it"
    # Remove fields that are enforced by license
    license_locked = load_license_overrides()
    for key, val in license_locked.items():
        data[key] = val
    with open(SETTINGS_FILE, "w") as fh:
        json.dump(data, fh)
    for pname, vals in plugin_updates.items():
        cfg_path = os.path.join(BASE_DIR, 'plugin', pname, 'settings.json')
        current = {}
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path) as fh:
                    current = json.load(fh)
            except Exception:
                pass
        current.update(vals)
        with open(cfg_path, 'w') as fh:
            json.dump(current, fh, indent=2)
    return data

def sanitize_email(email: str) -> str:
    return email.replace("@", "_at_").replace(".", "_")

def load_user_settings(email: str):
    base = load_settings()
    os.makedirs(USERS_DIR, exist_ok=True)
    path = os.path.join(USERS_DIR, sanitize_email(email) + ".json")
    if os.path.exists(path):
        try:
            with open(path) as fh:
                user = json.load(fh)
            base.update(user)
        except Exception:
            pass
    return base

def save_user_settings(email: str, update: dict):
    os.makedirs(USERS_DIR, exist_ok=True)
    path = os.path.join(USERS_DIR, sanitize_email(email) + ".json")
    data = {}
    if os.path.exists(path):
        try:
            with open(path) as fh:
                data = json.load(fh)
        except Exception:
            data = {}
    data.update(update)
    with open(path, "w") as fh:
        json.dump(data, fh)
    merged = load_settings()
    merged.update(data)
    return merged

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.auth.database import async_session_maker, init_db
    from fastapi_users.db import SQLAlchemyUserDatabase
    from app.utils.backup import backup_all

    # Ensure database and tables exist
    await init_db()

    # Create default admin user if none exists
    admin_email = os.getenv("DOCROPPER_ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("DOCROPPER_ADMIN_PASSWORD", "admin")
    async with async_session_maker() as session:
        user_db = SQLAlchemyUserDatabase(session, User)
        existing = await user_db.get_by_email(admin_email)
        if existing is None:
            hashed = bcrypt.hash(admin_password)
            admin = User(
                email=admin_email,
                hashed_password=hashed,
                is_active=True,
                is_superuser=True,
                is_verified=True,
            )
            session.add(admin)
            await session.commit()

    # Initial backup on start
    backup_all()
    try:
        yield
    finally:
        # Backup again on shutdown
        backup_all()

# Expose the OpenAPI schema and docs under the /api path so the Swagger UI
# fetches the specification from /api/openapi.json rather than the repository
# root. This avoids 404 errors when the FastAPI app is mounted under Django.
app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)
# Allow embedding the API in frames by forcing X-Frame-Options to SAMEORIGIN
@app.middleware("http")
async def set_frame_options(request, call_next):
    response = await call_next(request)
    # Some ASGI responses (e.g., from StaticFiles) may set a default
    # `X-Frame-Options: DENY`. Explicitly override this so that
    # documentation pages like the embedded guide can be displayed
    # inside iframes served from the same origin.
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response
# Only enable authentication routes when license checking is active
if load_settings().get("license_check", False):
    app.include_router(auth_router)

# Enable cross-origin requests if needed
origins = os.getenv("DOCROPPER_CORS_ORIGINS", "*")
if origins == "*":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    allowed = [o.strip() for o in origins.split(",") if o.strip()]
    if allowed:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

# Redirect bare ``/api`` requests to the interactive documentation.
# Returning an absolute path avoids ambiguities when the app is mounted under
# ``/api`` behind a dispatcher such as Django.
@app.get("/", include_in_schema=False)
async def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")


@app.get("", include_in_schema=False)
async def root_redirect_empty() -> RedirectResponse:
    return RedirectResponse(url="/api/docs")

# Dependency used to enforce that the configured license is valid
async def require_valid_license(
    request: Request,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
):
    settings = load_settings()
    if not settings.get("license_check", False):
        return user

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.license_token:
        raise HTTPException(status_code=403, detail="Token licenza mancante")

    domain = request.url.hostname
    data = await verify_license(
        user.email, user.license_type, user.license_token, domain
    )
    if not data.get("valid", False):
        raise HTTPException(status_code=403, detail="Licenza non valida")

    plugins = data.get("plugins", {})
    if isinstance(plugins, dict) and plugins:
        settings = load_settings()
        updates = {}
        for name, allowed in plugins.items():
            if name == "lan_users":
                try:
                    allowed_val = int(allowed)
                except (TypeError, ValueError):
                    continue
                if settings.get("lan_user_limit") != allowed_val:
                    updates["lan_user_limit"] = allowed_val
                continue
            key = f"enable_{name}"
            if settings.get(key) != allowed:
                updates[key] = allowed
        if updates:
            save_settings(updates)

    forced = data.get("settings", {})
    if isinstance(forced, dict) and forced:
        save_license_overrides(forced)

    settings = load_settings()
    limit = settings.get("lan_user_limit", 0)
    if limit and user.license_type == "pro":
        from sqlalchemy import select, func
        from app.auth.database import async_session_maker
        async with async_session_maker() as session:
            total = await session.scalar(select(func.count(User.id)))
        if total > limit:
            raise HTTPException(status_code=403, detail="LAN user limit exceeded")

    return user

# Mount static files directory and local wiki with no-cache headers
app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")
app.mount("/wiki", NoCacheStaticFiles(directory="wiki", html=True), name="wiki")
# Serve JavaScript helpers if present; fall back gracefully when the
# directory is missing so the API can start even without optional assets.
js_dir = Path("static/js")
if js_dir.is_dir():
    app.mount("/js", NoCacheStaticFiles(directory=str(js_dir)), name="js")
plugin_utils = {
    'load_settings': load_settings,
    'get_session_dir': get_session_dir,
    'get_lan_ip': get_lan_ip,
    'SIGNATURES_DIR': SIGNATURES_DIR,
    'decrypt_file': decrypt_file,
    'encrypt_bytes': encrypt_bytes,
    'ENC_SUFFIX': ENC_SUFFIX,
    'MAX_UPLOAD_BYTES': MAX_UPLOAD_BYTES,
}

settings = load_settings()
ACTIVE_PLUGINS: list[str] = []
key_upper = settings.get('license_key', '').strip().upper()
dev_env = DEV_LICENSE_KEY_UPPER
license_level = settings.get('license_level', '').strip().lower() or settings.get('license_type', '').strip().lower()
is_dev_license = (
    license_level == 'developer'
    or (dev_env and key_upper == dev_env)
    or key_upper.endswith('-DEV')
)

crop_dev = str(os.getenv('DOCROPPER_CROP_DEV_ONLY', settings.get('crop_dev_only', False))).lower() == 'true'
if not crop_dev or is_dev_license:
    register_crop(app, plugin_utils)
    ACTIVE_PLUGINS.append('crop')

enable_login = settings.get('license_check', False)
login_dev = str(os.getenv('DOCROPPER_LOGIN_DEV_ONLY', settings.get('login_dev_only', True))).lower() == 'true'
if enable_login and (not login_dev or is_dev_license):
    register_login(app, plugin_utils)
    ACTIVE_PLUGINS.append('login')

enable_sign = str(os.getenv('DOCROPPER_ENABLE_SIGN', settings.get('enable_sign', True))).lower() != 'false'
sign_dev = str(os.getenv('DOCROPPER_SIGN_DEV_ONLY', settings.get('sign_dev_only', False))).lower() == 'true'
enable_mobilesign = str(os.getenv('DOCROPPER_ENABLE_MOBILESIGN', settings.get('enable_mobilesign', False))).lower() == 'true'
mobilesign_dev = str(os.getenv('DOCROPPER_MOBILESIGN_DEV_ONLY', settings.get('mobilesign_dev_only', False))).lower() == 'true'
enable_remotesign = str(os.getenv('DOCROPPER_ENABLE_REMOTESIGN', settings.get('enable_remotesign', False))).lower() == 'true'
remotesign_dev = str(os.getenv('DOCROPPER_REMOTESIGN_DEV_ONLY', settings.get('remotesign_dev_only', True))).lower() == 'true'
enable_docuseal = str(os.getenv('DOCROPPER_ENABLE_DOCUSEAL', settings.get('enable_docuseal', False))).lower() == 'true'
docuseal_dev = str(os.getenv('DOCROPPER_DOCUSEAL_DEV_ONLY', settings.get('docuseal_dev_only', True))).lower() == 'true'
enable_removebg = str(os.getenv('DOCROPPER_ENABLE_REMOVEBG', settings.get('enable_removebg', False))).lower() == 'true'
removebg_dev = str(os.getenv('DOCROPPER_REMOVEBG_DEV_ONLY', settings.get('removebg_dev_only', False))).lower() == 'true'
enable_compresspdf = str(os.getenv('DOCROPPER_ENABLE_COMPRESSPDF', settings.get('enable_compresspdf', False))).lower() == 'true'
compresspdf_dev = str(os.getenv('DOCROPPER_COMPRESSPDF_DEV_ONLY', settings.get('compresspdf_dev_only', False))).lower() == 'true'
enable_watermark = str(os.getenv('DOCROPPER_ENABLE_WATERMARK', settings.get('enable_watermark', False))).lower() == 'true'
watermark_dev = str(os.getenv('DOCROPPER_WATERMARK_DEV_ONLY', settings.get('watermark_dev_only', False))).lower() == 'true'
enable_downloadpng = str(os.getenv('DOCROPPER_ENABLE_DOWNLOADPNG', settings.get('enable_downloadpng', False))).lower() == 'true'
downloadpng_dev = str(os.getenv('DOCROPPER_DOWNLOADPNG_DEV_ONLY', settings.get('downloadpng_dev_only', True))).lower() == 'true'
enable_pageselect = str(os.getenv('DOCROPPER_ENABLE_PAGESELECT', settings.get('enable_pageselect', True))).lower() == 'true'
pageselect_dev = str(os.getenv('DOCROPPER_PAGESELECT_DEV_ONLY', settings.get('pageselect_dev_only', False))).lower() == 'true'
enable_colormode = str(os.getenv('DOCROPPER_ENABLE_COLORMODE', settings.get('enable_colormode', True))).lower() == 'true'
colormode_dev = str(os.getenv('DOCROPPER_COLORMODE_DEV_ONLY', settings.get('colormode_dev_only', False))).lower() == 'true'
enable_imageeditor = str(os.getenv('DOCROPPER_ENABLE_IMAGEEDITOR', settings.get('enable_imageeditor', True))).lower() == 'true'
imageeditor_dev = str(os.getenv('DOCROPPER_IMAGEEDITOR_DEV_ONLY', settings.get('imageeditor_dev_only', True))).lower() == 'true'
enable_formfields = str(os.getenv('DOCROPPER_ENABLE_FORMFIELDS', settings.get('enable_formfields', False))).lower() == 'true'
formfields_dev = str(os.getenv('DOCROPPER_FORMFIELDS_DEV_ONLY', settings.get('formfields_dev_only', True))).lower() == 'true'
enable_scan = str(os.getenv('DOCROPPER_ENABLE_SCAN', settings.get('enable_scan', False))).lower() == 'true'
scan_dev = str(os.getenv('DOCROPPER_SCAN_DEV_ONLY', settings.get('scan_dev_only', True))).lower() == 'true'
enable_cloudsave = str(os.getenv('DOCROPPER_ENABLE_CLOUDSAVE', settings.get('enable_cloudsave', False))).lower() == 'true'
cloudsave_dev = str(os.getenv('DOCROPPER_CLOUDSAVE_DEV_ONLY', settings.get('cloudsave_dev_only', True))).lower() == 'true'

if enable_sign and (not sign_dev or is_dev_license):
    register_sign(app, plugin_utils)
    ACTIVE_PLUGINS.append('sign')
if enable_mobilesign and (not mobilesign_dev or is_dev_license):
    register_mobilesign(app, plugin_utils)
    ACTIVE_PLUGINS.append('mobilesign')
if enable_remotesign and (not remotesign_dev or is_dev_license):
    register_remotesign(app, plugin_utils)
    ACTIVE_PLUGINS.append('remotesign')
if enable_docuseal and (not docuseal_dev or is_dev_license):
    register_docuseal(app, plugin_utils)
    ACTIVE_PLUGINS.append('docuseal')
if enable_removebg and (not removebg_dev or is_dev_license):
    register_removebg(app, plugin_utils)
    ACTIVE_PLUGINS.append('removebg')
if enable_compresspdf and (not compresspdf_dev or is_dev_license) and settings.get('license_level', 'free').lower() != 'free':
    register_compresspdf(app, plugin_utils)
    ACTIVE_PLUGINS.append('compresspdf')
if enable_watermark and (not watermark_dev or is_dev_license):
    register_watermark(app, plugin_utils)
    ACTIVE_PLUGINS.append('watermark')
if enable_downloadpng and (not downloadpng_dev or is_dev_license):
    register_downloadpng(app, plugin_utils)
    ACTIVE_PLUGINS.append('downloadpng')
if enable_pageselect and (not pageselect_dev or is_dev_license):
    register_pageselect(app, plugin_utils)
    ACTIVE_PLUGINS.append('pageselect')
if enable_colormode and (not colormode_dev or is_dev_license):
    register_colormode(app, plugin_utils)
    ACTIVE_PLUGINS.append('colormode')
if enable_imageeditor and (not imageeditor_dev or is_dev_license):
    from plugin.core.imageeditor import register as register_imageeditor
    register_imageeditor(app, plugin_utils)
    ACTIVE_PLUGINS.append('imageeditor')
if enable_formfields and (not formfields_dev or is_dev_license):
    from plugin.core.formfields import register as register_formfields
    register_formfields(app, plugin_utils)
    ACTIVE_PLUGINS.append('formfields')
if enable_scan and (not scan_dev or is_dev_license):
    register_scan(app, plugin_utils)
    ACTIVE_PLUGINS.append('scan')
if enable_cloudsave and (not cloudsave_dev or is_dev_license):
    register_cloudsave(app, plugin_utils)
    ACTIVE_PLUGINS.append('cloudsave')

@app.get("/me", tags=["auth"])
async def get_me(user: User = Depends(fastapi_users.current_user())):
    return {"email": user.email, "license": user.license_type}

@app.get('/favicon.ico')
async def favicon():
    icon_path = os.path.join(os.path.dirname(__file__), 'static', 'logos', 'app_logo.png')
    return FileResponse(icon_path, headers={"Cache-Control": "no-cache"})

def make_index_response(request: Request, lang: str) -> HTMLResponse:
    cleanup_old_sessions()
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = uuid.uuid4().hex
    get_session_dir(session_id)
    try:
        base_dir = os.path.dirname(__file__)
        template_name = load_settings().get("template", "static")
        if isinstance(template_name, str):
            template_name = template_name.strip().lower()
        else:
            template_name = "static"

        index_path = os.path.join(base_dir, "static", "index.html")
        if template_name != "static":
            alt_path = os.path.join(base_dir, "templates", template_name, "index.html")
            if os.path.exists(alt_path):
                index_path = alt_path
            else:
                logger.error("Template '%s' not found, using static index", template_name)

        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace('<html lang="en">', f'<html lang="{lang}">')
        content = content.replace('</head>', f'<script>window.DC_LANG="{lang}";</script></head>')
        cache_bust = get_cache_bust()
        if cache_bust:
            content = content.replace("styles.css", f"styles.css{cache_bust}")
            content = content.replace("app.js", f"app.js{cache_bust}")
            content = content.replace("mobilesign.js", f"mobilesign.js{cache_bust}")
            content = content.replace("app_logo.png", f"app_logo.png{cache_bust}")
            content = content.replace("header_logo.png", f"header_logo.png{cache_bust}")
            content = content.replace("footer_logo.png", f"footer_logo.png{cache_bust}")
            content = content.replace("DocCropper_slogan_main_en.png", f"DocCropper_slogan_main_en.png{cache_bust}")
            content = content.replace("DocCropper_slogan_main_it.png", f"DocCropper_slogan_main_it.png{cache_bust}")
            content = content.replace("DocCropper_slogan_sign_en.png", f"DocCropper_slogan_sign_en.png{cache_bust}")
            content = content.replace("DocCropper_slogan_sign_it.png", f"DocCropper_slogan_sign_it.png{cache_bust}")
    except FileNotFoundError:
        logger.error(f"{index_path} not found")
        return HTMLResponse(content="Frontend not found.", status_code=500)
    response = HTMLResponse(content=content, status_code=200)
    # Ensure the HTML itself is never cached so new bundle versions load
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.set_cookie("session_id", session_id, httponly=True)
    return response


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    lang = load_settings().get("language", "it")
    return make_index_response(request, lang)


@app.get("/{lang:en|it}", response_class=HTMLResponse)
async def read_root_lang(lang: str, request: Request):
    return make_index_response(request, lang)


async def require_superuser(user: User = Depends(fastapi_users.current_user())):
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(user: User = Depends(require_superuser)):
    try:
        path = os.path.join(os.path.dirname(__file__), "static", "admin.html")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        cache_bust = get_cache_bust()
        if cache_bust:
            content = content.replace("styles.css", f"styles.css{cache_bust}")
            content = content.replace("admin.js", f"admin.js{cache_bust}")
    except FileNotFoundError:
        return HTMLResponse(content="Admin page not found", status_code=404)
    return HTMLResponse(content=content, status_code=200)



@app.get("/settings/")
async def get_settings():
    data = load_settings()
    if not data.get("license_check") and not data.get("license_key"):
        data["license_key"] = "FREE"
        data["license_name"] = "Free Edition"
    version, version_date = get_version_info()
    data["version"] = version
    data["version_date"] = version_date
    data["active_plugins"] = ACTIVE_PLUGINS
    if "stripe_secret_key" in data:
        data.pop("stripe_secret_key")
    return JSONResponse(data, headers={"Cache-Control": "no-store, max-age=0"})


@app.post("/settings/")
async def update_settings(settings: dict = Body(...)):
    data = save_settings(settings)
    return JSONResponse(data, headers={"Cache-Control": "no-store, max-age=0"})


@app.get("/user-settings/")
async def get_user_settings_endpoint(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        return JSONResponse(status_code=401, content={"message": "Not logged in"})
    data = load_user_settings(email)
    version, version_date = get_version_info()
    data["version"] = version
    data["version_date"] = version_date
    return JSONResponse(data, headers={"Cache-Control": "no-store, max-age=0"})


@app.post("/user-settings/")
async def update_user_settings_endpoint(request: Request, settings: dict = Body(...)):
    email = request.cookies.get("user_email")
    if not email:
        return JSONResponse(status_code=401, content={"message": "Not logged in"})
    data = save_user_settings(email, settings)
    version, version_date = get_version_info()
    data["version"] = version
    data["version_date"] = version_date
    return JSONResponse(data, headers={"Cache-Control": "no-store, max-age=0"})


@app.post("/license/manual")
async def set_manual_license(data: dict = Body(...)):
    key = (data.get("key") or "").strip()
    name = (data.get("name") or "").strip()
    if not key:
        raise HTTPException(status_code=400, detail="Missing key")
    os.makedirs(ENV_DIR, exist_ok=True)
    env_path = os.path.join(ENV_DIR, "license.env")
    try:
        with open(env_path, "w", encoding="utf-8") as fh:
            fh.write(
                f"DOCROPPER_MANUAL_LICENSE={key}\n"
                f"DOCROPPER_LICENSE_KEY={key}\n"
                f"DOCROPPER_LICENSE_NAME={name}\n"
                "LICENSE_CHECK=false\n"
            )
            fh.flush()
            os.fsync(fh.fileno())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to write license: {exc}")
    load_env_files(override=True)
    global DEV_LICENSE_KEY, DEV_LICENSE_KEY_UPPER, MANUAL_LICENSE_KEY, ONLINE_LICENSE_KEY
    DEV_LICENSE_KEY = os.environ.get("DOCROPPER_DEV_LICENSE", DEV_LICENSE_KEY)
    DEV_LICENSE_KEY_UPPER = DEV_LICENSE_KEY.upper()
    MANUAL_LICENSE_KEY = os.environ.get("DOCROPPER_MANUAL_LICENSE", MANUAL_LICENSE_KEY).upper()
    ONLINE_LICENSE_KEY = os.environ.get("DOCROPPER_ONLINE_LICENSE", ONLINE_LICENSE_KEY).upper()
    saved = save_settings({"license_key": key, "license_name": name, "license_check": False})
    for p in Path(BASE_DIR).rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
    for p in Path(BASE_DIR).rglob("*.pyc"):
        try:
            p.unlink()
        except Exception:
            pass
    return JSONResponse(
        {"status": "saved", "license_key": key, "license_name": name},
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.post("/license/upload")
async def upload_license(request: Request, file: UploadFile = File(...)):
    token = (await file.read()).decode("utf-8").strip()
    try:
        payload = jwt.decode(token, LICENSE_SECRET, algorithms=["HS256"])
        now = int(time.time())
        exp = payload.get("expires_at")
        if exp and exp < now:
            raise HTTPException(status_code=400, detail="Token expired")
        allowed = payload.get("allowed_domains")
        domain = request.client.host
        if allowed and domain not in allowed:
            raise HTTPException(status_code=403, detail="Domain not allowed")
    except JWTError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid token: {exc}")

    name = payload.get("license_name", "")
    ltype = payload.get("license_type", "manual")
    os.makedirs(ENV_DIR, exist_ok=True)
    env_path = os.path.join(ENV_DIR, "license.env")
    try:
        with open(env_path, "w", encoding="utf-8") as fh:
            fh.write(
                f"DOCROPPER_LICENSE_TOKEN={token}\n"
                f"DOCROPPER_LICENSE_NAME={name}\n"
                f"DOCROPPER_LICENSE_TYPE={ltype}\n"
                "LICENSE_CHECK=false\n"
            )
            fh.flush()
            os.fsync(fh.fileno())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to write license: {exc}")

    load_env_files(override=True)
    saved = save_settings(
        {
            "license_token": token,
            "license_name": name,
            "license_type": ltype,
            "license_level": "full",
            "license_check": False,
        }
    )
    for p in Path(BASE_DIR).rglob("__pycache__"):
        shutil.rmtree(p, ignore_errors=True)
    for p in Path(BASE_DIR).rglob("*.pyc"):
        try:
            p.unlink()
        except Exception:
            pass
    return JSONResponse(
        {"status": "saved", "license_name": name, "license_type": ltype},
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.get("/license/status")
async def license_status(request: Request):
    settings = load_settings()
    valid = True
    if settings.get("license_check", False):
        domain = request.headers.get("host")
        try:
            data = await verify_license("", settings.get("license_type", ""), settings.get("license_key", ""), domain)
            valid = bool(data.get("valid"))
        except Exception:
            valid = False
    info = {
        "license_key": settings.get("license_key", ""),
        "license_name": settings.get("license_name", ""),
        "license_token": settings.get("license_token", ""),
        "license_level": settings.get("license_level", "free"),
        "license_type": settings.get("license_type", "free"),
        "valid": valid,
    }
    return JSONResponse(info, headers={"Cache-Control": "no-store, max-age=0"})


@app.post("/clear-session/")
async def clear_session(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id:
        session_dir = os.path.join(SESSIONS_ROOT, session_id)
        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir, ignore_errors=True)
        SESSION_KEYS.pop(session_id, None)
    return {"status": "ok"}


@app.get("/updates/")
async def get_updates():
    path = os.path.join(os.path.dirname(__file__), "UPDATES.md")
    if not os.path.exists(path):
        return {"en": [], "it": []}
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        current_date = ""
        for line in fh:
            line = line.strip()
            if line.startswith("##"):
                current_date = line.lstrip("# ").strip()
            elif line.startswith("- ") and current_date:
                entries.append(f"{current_date}: {line[2:].strip()}")
    return {"en": entries, "it": entries}


@app.get("/update-check/")
async def update_check():
    return {"available": repo_has_updates()}


@app.post("/update/")
async def update_app(data: dict = Body(...)):
    pin = data.get("pin", "")
    settings = load_settings()
    if pin != settings.get("update_pin", ""):
        raise HTTPException(status_code=403, detail="Invalid PIN")
    run_update_script()
    return {"status": "started"}


@app.post("/rollback/")
async def rollback_app(data: dict = Body(...)):
    pin = data.get("pin", "")
    settings = load_settings()
    if pin != settings.get("update_pin", ""):
        raise HTTPException(status_code=403, detail="Invalid PIN")
    run_rollback_script()
    return {"status": "started"}


@app.post("/developer-login/")
async def developer_login(data: dict = Body(...)):
    password = data.get("password", "")
    settings = load_settings()
    hashed = settings.get("developer_password_hash", "")
    if hashed and bcrypt.verify(password, hashed):
        if bcrypt.verify(DEFAULT_DEV_PASSWORD, hashed):
            raise HTTPException(status_code=403, detail="Change default developer password")
        return {"status": "ok"}
    raise HTTPException(status_code=403, detail="Invalid password")


@app.post("/developer-password/")
async def change_developer_password(data: dict = Body(...)):
    old = data.get("old", "")
    new = data.get("new", "")
    if not new:
        raise HTTPException(status_code=400, detail="New password required")
    settings = load_settings()
    hashed = settings.get("developer_password_hash", "")
    if not hashed or not bcrypt.verify(old, hashed):
        raise HTTPException(status_code=403, detail="Invalid password")
    save_settings({"developer_password_hash": bcrypt.hash(new)})
    return {"status": "updated"}


@app.post("/settings-login/")
async def settings_login(data: dict = Body(...)):
    password = data.get("password", "")
    settings = load_settings()
    hashed = settings.get("settings_password_hash", "")
    if hashed and bcrypt.verify(password, hashed):
        if bcrypt.verify(DEFAULT_SETTINGS_PASSWORD, hashed):
            raise HTTPException(status_code=403, detail="Change default settings password")
        return {"status": "ok"}
    raise HTTPException(status_code=403, detail="Invalid password")


@app.post("/settings-password/")
async def change_settings_password(data: dict = Body(...)):
    old = data.get("old", "")
    new = data.get("new", "")
    if not new:
        raise HTTPException(status_code=400, detail="New password required")
    settings = load_settings()
    hashed = settings.get("settings_password_hash", "")
    if not hashed or not bcrypt.verify(old, hashed):
        raise HTTPException(status_code=403, detail="Invalid password")
    save_settings({"settings_password_hash": bcrypt.hash(new)})
    return {"status": "updated"}


@app.post("/stripe-checkout/")
async def stripe_checkout(level: str = Body(...)):
    settings = load_settings()
    if stripe is None:
        return JSONResponse(status_code=503, content={"message": "Stripe library missing"})
    secret = settings.get("stripe_secret_key")
    if not secret:
        return JSONResponse(status_code=503, content={"message": "Stripe not configured"})
    if level not in ("pro", "full"):
        return JSONResponse(status_code=400, content={"message": "Invalid license"})
    price_id = settings.get("stripe_price_pro") if level == "pro" else settings.get("stripe_price_full")
    if not price_id:
        return JSONResponse(status_code=503, content={"message": "Price ID missing"})
    stripe.api_key = secret
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=settings.get("stripe_success_url") or "https://example.com/success",
            cancel_url=settings.get("stripe_cancel_url") or "https://example.com/cancel",
        )
        return {"session_url": session.url}
    except Exception as e:
        logger.exception("Stripe session creation failed")
        return JSONResponse(status_code=500, content={"message": str(e)})


@app.post("/stripe-webhook/")
async def stripe_webhook(request: Request):
    if stripe is None:
        return JSONResponse(status_code=503, content={"message": "Stripe library missing"})
    settings = load_settings()
    webhook_secret = settings.get("stripe_webhook_secret")
    if not webhook_secret:
        return JSONResponse(status_code=503, content={"message": "Stripe not configured"})
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception:
        return JSONResponse(status_code=400, content={"message": "Invalid payload"})
    if event.get("type") == "checkout.session.completed":
        session = event.get("data", {}).get("object", {})
        if session.get("payment_status") != "paid":
            return JSONResponse(status_code=400, content={"message": "Payment not completed"})
        # License generation would occur here
    return {"received": True}


@app.post("/pdf-to-images/")
async def pdf_to_images(
    request: Request,
    pdf_file: UploadFile = File(...),
    threshold: int = Form(95),
    skip_blank: bool = Form(True)
):
    """Convert PDF pages to base64 PNG images."""
    settings = load_settings()
    if settings.get("license_level", "free").lower() == "free":
        return JSONResponse(status_code=403, content={"message": "PDF import requires Pro license"})
    try:
        pdf_bytes = await pdf_file.read()
        if len(pdf_bytes) > MAX_UPLOAD_BYTES:
            return JSONResponse(status_code=413, content={"message": "File too large"})

        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = uuid.uuid4().hex
        session_dir = get_session_dir(session_id)
        if session_dir:
            try:
                fname = os.path.join(session_dir, f"{uuid.uuid4().hex}.pdf{ENC_SUFFIX}")
                enc_pdf = encrypt_bytes(session_id, pdf_bytes)
                with open(fname, "wb") as fh:
                    fh.write(enc_pdf)
            except Exception:
                logger.exception("Failed to save uploaded PDF")

        fitz = get_fitz()
        np = get_np()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        thr = max(0, min(100, int(threshold))) / 100.0
        images_b64: list[str] = []
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            gray = np.array(img.convert("L"))
            if skip_blank and np.mean(gray > 240) >= thr:
                continue
            img_bytes = pix.tobytes("png")
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            images_b64.append("data:image/png;base64," + b64)
        return {"images": images_b64}
    except Exception as e:
        logger.exception("Failed to convert PDF")
        return JSONResponse(status_code=500, content={"message": f"PDF conversion failed: {str(e)}"})


@app.post("/create-pdf/", dependencies=[Depends(require_valid_license)])
async def create_pdf(
    request: Request,
    images: list[str] = Body(...),
    layout: int = Body(1),
    orientation: str = Body("portrait"),
    arrangement: str = Body("auto"),
    scale_mode: str = Body("fit"),
    scale_percent: int = Body(100),
    color_mode: str = Body("color"),
    signature_image: str | None = Body(None),
    remove_signature_bg: bool = Body(True),
    signatures: list[dict] = Body(default_factory=list),
    sign_info: dict | None = Body(default_factory=dict),
    compression: str = Body("none"),
    jpeg_quality: int = Body(75),
    pdfa_version: int | None = Body(None),
):
    try:
        settings = load_settings()
        key = settings.get("license_key", "").strip().upper()
        license_check = settings.get("license_check", False)
        dev_env = DEV_LICENSE_KEY_UPPER
        dev_key_valid = dev_env and key == dev_env
        demo_key = key == DEMO_FULL_LICENSE_KEY
        if license_check:
            if demo_key:
                licensed = False
            elif dev_key_valid:
                licensed = True
            elif key:
                licensed = verify_license_server(key)
            else:
                licensed = False
        else:
            licensed = True
            if demo_key or (dev_key_valid and settings.get("developer_watermark", False)):
                licensed = False
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = uuid.uuid4().hex
        session_dir = get_session_dir(session_id)
        pil_images = []
        for img_b64 in images:
            if img_b64.startswith('data:'):
                img_b64 = img_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(img_b64)
            pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            pil_images.append(pil_img)

        if color_mode.lower() in ("gray", "bw"):
            converted = []
            for img in pil_images:
                gray = img.convert("L")
                if color_mode.lower() == "bw":
                    bw = gray.point(lambda x: 0 if x < 128 else 255, "1")
                    converted.append(bw.convert("RGB"))
                else:
                    converted.append(gray.convert("RGB"))
            pil_images = converted

        sig_img = None
        if signature_image:
            try:
                sig_b64 = signature_image.split(',', 1)[1] if signature_image.startswith('data:') else signature_image
                sig_bytes = base64.b64decode(sig_b64)
                sig_img = Image.open(io.BytesIO(sig_bytes)).convert('RGBA')
                if remove_signature_bg:
                    np = get_np()
                    arr = np.array(sig_img)
                    white = (arr[:, :, :3] > 240).all(axis=2)
                    arr[white, 3] = 0
                    sig_img = Image.fromarray(arr)
            except Exception:
                logger.exception('Failed to decode signature image')

        if not pil_images:
            return JSONResponse(status_code=400, content={"message": "No images provided"})

        layout = max(1, layout)
        if layout not in (1, 2, 4):
            layout = 1

        arrangement = arrangement.lower()
        if arrangement not in ("auto", "vertical", "horizontal", "grid"):
            arrangement = "auto"

        orientation = orientation.lower()
        if orientation not in ("portrait", "landscape"):
            orientation = "portrait"

        cols = 1
        rows = 1
        if layout == 2:
            if arrangement == "horizontal":
                cols, rows = 2, 1
            elif arrangement == "vertical":
                cols, rows = 1, 2
            else:  # auto
                if orientation == "landscape":
                    cols, rows = 2, 1
                else:
                    cols, rows = 1, 2
        elif layout == 4:
            if arrangement == "horizontal":
                cols, rows = 4, 1
            elif arrangement == "vertical":
                cols, rows = 1, 4
            else:  # grid or auto
                cols, rows = 2, 2

        if orientation == "portrait":
            page_w, page_h = 2480, 3508
        else:
            page_w, page_h = 3508, 2480

        scale_mode = scale_mode.lower()
        if scale_mode not in ("fit", "original", "percent"):
            scale_mode = "fit"
        cell_w = page_w // cols
        cell_h = page_h // rows
        margin = 40  # pixels of padding around each image
        inner_w = max(1, cell_w - margin * 2)
        inner_h = max(1, cell_h - margin * 2)

        header_logo = None
        footer_logo = None
        if not licensed:
            logos_dir = os.path.join(os.path.dirname(__file__), "static", "logos")
            try:
                header_logo = Image.open(os.path.join(logos_dir, "header_logo.png")).convert("RGBA")
            except Exception:
                header_logo = None
            try:
                footer_logo = Image.open(os.path.join(logos_dir, "footer_logo.png")).convert("RGBA")
            except Exception:
                footer_logo = None


        pages = []
        TARGET_DPI = 300
        for i in range(0, len(pil_images), layout):
            page_index = i // layout
            page = Image.new("RGB", (page_w, page_h), "white")
            placements: list[tuple[int, int, int, int]] = []
            for j, img in enumerate(pil_images[i:i+layout]):
                col = j % cols
                row = j // cols
                temp = img.copy()

                img_dpi = temp.info.get("dpi", (72, 72))[0] or 72
                dpi_ratio = TARGET_DPI / img_dpi

                if scale_mode == "percent":
                    ratio = max(0.01, scale_percent / 100.0) * dpi_ratio
                elif scale_mode == "fit":
                    ratio = min(inner_w / temp.width, inner_h / temp.height)
                else:  # original
                    ratio = dpi_ratio

                max_ratio = min(inner_w / temp.width, inner_h / temp.height)
                if ratio > max_ratio:
                    ratio = max_ratio

                new_w = max(1, int(temp.width * ratio))
                new_h = max(1, int(temp.height * ratio))
                temp = temp.resize((new_w, new_h), Image.LANCZOS)
                offset_x = col * cell_w + margin + (inner_w - new_w) // 2
                offset_y = row * cell_h + margin + (inner_h - new_h) // 2
                page.paste(temp, (offset_x, offset_y))
                placements.append((offset_x, offset_y, new_w, new_h))
            if not licensed:
                target_h = page_h // 35
                hl = fl = None
                if header_logo:
                    ratio = target_h / header_logo.height
                    hl = header_logo.resize((int(header_logo.width * ratio), target_h), Image.LANCZOS)
                if footer_logo:
                    ratio = target_h / footer_logo.height
                    fl = footer_logo.resize((int(footer_logo.width * ratio), target_h), Image.LANCZOS)
                draw = ImageDraw.Draw(page)
                if hl:
                    hx = margin
                    hy = page_h - hl.height - margin
                    page.paste(hl, (hx, hy), hl)
                if fl:
                    fx = page_w - fl.width - margin
                    fy = page_h - fl.height - margin
                    text = "by IlTuoConsulenteIT"
                    font_size = max(10, fl.height // 2)
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                    except Exception:
                        font = ImageFont.load_default()
                    if hasattr(draw, "textbbox"):
                        bbox = draw.textbbox((0, 0), text, font=font)
                        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    else:
                        tw, th = font.getsize(text)
                    tx = fx - tw - 5
                    ty = fy + (fl.height - th) // 2
                    draw.text((tx, ty), text, fill="black", font=font)
                    page.paste(fl, (fx, fy), fl)
            if sig_img and signatures and placements:
                footer_h = fl.height if (not licensed and fl) else 0
                img_off_x, img_off_y, img_w, img_h = placements[0]
                base_ratio = (img_h // 10) / sig_img.height
                for sig in [s for s in signatures if s.get('page') == page_index]:
                    try:
                        scale = float(sig.get('scale', 1.0))
                    except Exception:
                        scale = 1.0
                    w = int(sig_img.width * base_ratio * scale)
                    h = int(sig_img.height * base_ratio * scale)
                    stamp = sig_img.resize((w, h), Image.LANCZOS)
                    sx = int(img_off_x + float(sig.get('x', 0.5)) * img_w - w / 2)
                    sy = int(img_off_y + float(sig.get('y', 0.5)) * img_h - h / 2)
                    if sx < margin:
                        sx = margin
                    if sy < margin:
                        sy = margin
                    if sx + w > page_w - margin:
                        sx = page_w - margin - w
                    if sy + h > page_h - margin - footer_h:
                        sy = page_h - margin - footer_h - h
                    page.paste(stamp, (sx, sy), stamp)
            pages.append(page)

        if sign_info:
            log_page = Image.new("RGB", (page_w, page_h), "white")
            draw = ImageDraw.Draw(log_page)
            try:
                log_font = ImageFont.truetype("DejaVuSans.ttf", 40)
            except Exception:
                log_font = ImageFont.load_default()
            y = 100
            ts = sign_info.get("timestamp") or datetime.utcnow().isoformat()
            lines = [f"Signed on: {ts}"]
            if sign_info.get("email"):
                lines.append(f"Email: {sign_info['email']}")
            if sign_info.get("phone"):
                lines.append(f"Phone: {sign_info['phone']}")
            if 'consent' in sign_info:
                lines.append(f"Consent: {bool(sign_info['consent'])}")
            for idx, sig in enumerate(signatures, 1):
                lines.append(
                    f"Signature {idx}: page {sig.get('page', 0)+1} x={sig.get('x',0):.2f} y={sig.get('y',0):.2f} scale={sig.get('scale',1)}"
                )
            for line in lines:
                draw.text((100, y), line, fill="black", font=log_font)
                y += log_font.getsize(line)[1] + 20
            pages.append(log_page)

        pdf_bytes_io = io.BytesIO()
        pages[0].save(pdf_bytes_io, format="PDF", save_all=True, append_images=pages[1:])
        pdf_bytes = pdf_bytes_io.getvalue()

        cert_path = os.environ.get("DOCROPPER_SIGN_CERT")
        cert_password = os.environ.get("DOCROPPER_SIGN_PASSWORD")
        if cert_path and signers:
            try:
                signer = signers.SimpleSigner.load_pkcs12(cert_path, cert_password.encode() if cert_password else None)
                pdf_signer = signers.PdfSigner(signers.PdfSignatureMetadata(field_name="DocCropperSig"), signer=signer)
                signed_io = io.BytesIO()
                pdf_signer.sign_pdf(io.BytesIO(pdf_bytes), signed_io)
                pdf_bytes = signed_io.getvalue()
            except Exception:
                logger.exception("PDF signing failed")
        compressor = plugin_utils.get("compress_pdf")
        if compressor and (compression and compression.lower() != "none"):
            pdf_bytes = compressor(pdf_bytes, compression, jpeg_quality)
        if pdfa_version is not None:
            try:
                fitz = get_fitz()
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pdf_bytes = doc.tobytes(deflate=True, clean=True, garbage=4, pdfa=int(pdfa_version) - 1)
            except Exception:
                logger.exception("PDF/A conversion failed")

        pdf_path = os.path.join(session_dir, "output.pdf" + ENC_SUFFIX)
        try:
            enc = encrypt_bytes(session_id, pdf_bytes)
            with open(pdf_path, "wb") as fh:
                fh.write(enc)
        except Exception:
            logger.exception("Failed to save PDF")
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        cleanup_old_sessions()
        response = JSONResponse(content={"pdf": "data:application/pdf;base64," + pdf_base64})
        response.set_cookie("session_id", session_id, httponly=True)
        return response
    except Exception as e:
        logger.exception("Failed to create PDF")
        return JSONResponse(status_code=500, content={"message": f"Could not create PDF: {str(e)}"})




@app.post("/ocr/")
async def extract_text(request: Request, images: list[str] = Body(...)):
    if pytesseract is None:
        return JSONResponse(status_code=503, content={"message": "OCR not available"})
    try:
        settings = load_settings()
        lang = settings.get("language", "it")
        text_parts = []
        for img_b64 in images:
            if img_b64.startswith('data:'):
                img_b64 = img_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(img_b64)
            np = get_np()
            cv2 = get_cv2()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_cv = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img_cv is None:
                continue
            try:
                text_parts.append(pytesseract.image_to_string(img_cv, lang=lang))
            except Exception:
                logger.exception("OCR failed for one image")
        return {"text": "\n".join(text_parts)}
    except Exception as e:
        logger.exception("OCR extraction error")
        return JSONResponse(status_code=500, content={"message": f"OCR failed: {str(e)}"})


@app.post("/shutdown/")
async def shutdown():
    server = getattr(app.state, "server", None)
    if server:
        server.should_exit = True
        return {"message": "Shutting down"}
    return {"message": "Server not running"}


@app.post("/restart/")
async def restart():
    server = getattr(app.state, "server", None)
    python = sys.executable
    args = [python] + sys.argv
    subprocess.Popen(args)
    if server:
        server.should_exit = True
        return {"message": "Restarting"}
    return {"message": "Server not running"}

if __name__ == "__main__":
    import argparse
    import signal

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
    port = args.port if args.port is not None else int(settings.get("port", 8765))
    host = args.host
    if settings.get("license_level", "free").lower() != "full":
        dev_env = DEV_LICENSE_KEY_UPPER
        key = settings.get("license_key", "").strip().upper()
        if not (dev_env and key == dev_env):
            host = "127.0.0.1"

    config = uvicorn.Config(app, host=host, port=port, forwarded_allow_ips="*")
    server = uvicorn.Server(config)
    app.state.server = server
    with open(PID_FILE, "w") as fh:
        fh.write(str(os.getpid()))
    try:
        server.run()
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
