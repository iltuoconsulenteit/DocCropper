import base64
import io
import logging
import json
import math
import os
import shutil
import time
import uuid
from datetime import datetime

import cv2
import numpy as np
import fitz
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, Body, Request, Depends, HTTPException
from PIL import Image, ImageDraw, ImageFont
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles


class NoCacheStaticFiles(StaticFiles):
    """StaticFiles that sets no-cache headers to avoid proxy caching."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = "no-cache"
            response.headers["Pragma"] = "no-cache"
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
from plugins.sign import register as register_sign
from app.licensing.check import verify_license
from app.auth.routes import router as auth_router, fastapi_users
from app.auth.models import User
from plugins.mobilesign import register as register_mobilesign
from plugins.remotesign import register as register_remotesign
from plugins.crop import register as register_crop
from plugins.removebg import register as register_removebg
from plugins.compresspdf import register as register_compresspdf

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


SETTINGS_FILE = "settings.json"
# Additional file storing values enforced by a license check
LICENSE_OVERRIDES_FILE = "license_overrides.json"
# Load environment variables from any .env files in env/
ENV_DIR = "env"
if os.path.isdir(ENV_DIR):
    for name in os.listdir(ENV_DIR):
        if name.endswith(".env"):
            load_dotenv(os.path.join(ENV_DIR, name), override=False)
# Directory containing per-user settings
USERS_DIR = "users"

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
DEV_LICENSE_KEY = os.environ.get("DOCROPPER_DEV_LICENSE", "")
DEV_LICENSE_KEY_UPPER = DEV_LICENSE_KEY.upper()
DEMO_FULL_LICENSE_KEY = "DEMO-FULL-DC"

try:
    VERSION = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=os.path.dirname(__file__),
        stderr=subprocess.DEVNULL,
    ).decode().strip()
    VERSION_DATE = subprocess.check_output(
        ["git", "log", "-1", "--format=%cd", "--date=short"],
        cwd=os.path.dirname(__file__),
        stderr=subprocess.DEVNULL,
    ).decode().strip()
except Exception:
    VERSION = "unknown"
    VERSION_DATE = ""

CACHE_BUST = f"?v={VERSION}"

SESSIONS_ROOT = "sessions"
SIGNATURES_DIR = "signatures"
PID_FILE = os.path.join(tempfile.gettempdir(), "doccropper.pid")
ENC_SUFFIX = ".enc"
SESSION_KEYS: dict[str, bytes] = {}
MAX_UPLOAD_MB = int(os.getenv("DOCROPPER_MAX_UPLOAD_MB", "20"))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

DEFAULT_SETTINGS = {
    "language": "en",
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
    "sponsor_scale": 100,
    "sponsor_bottom": 80,
    "brand_height": 80,
    "brand_gap": 20,
    "blank_threshold": 95,
    "skip_blank": True,
    "max_upload_files": 10,
    "enable_sponsor_video": False,
    "banner_images": ["DocCropper_slogan_{{lang}}.png"],
    "developer_watermark": False,
    "demo_full_mode": False,
    "docuseal_api_url": "",
    "docuseal_api_key": "",
    "public_url": "",
    "template": "static",
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
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as fh:
            json.dump(DEFAULT_SETTINGS, fh)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE) as fh:
            base = json.load(fh)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(base)
        env_key = os.getenv("DOCROPPER_LICENSE_KEY")
        env_name = os.getenv("DOCROPPER_LICENSE_NAME")
        google_id = os.getenv("DOCROPPER_GOOGLE_CLIENT_ID")
        env_check = os.getenv("LICENSE_CHECK")
        env_level = os.getenv("DOCROPPER_LICENSE_LEVEL")
        dev_wm_env = os.getenv("DOCROPPER_DEV_WATERMARK")
        docuseal_url = os.getenv("DOCUSEAL_API_URL")
        docuseal_key = os.getenv("DOCUSEAL_API_KEY")
        stripe_secret = os.getenv("STRIPE_SECRET_KEY")
        stripe_publish = os.getenv("STRIPE_PUBLISHABLE_KEY")
        stripe_pro = os.getenv("STRIPE_PRICE_PRO")
        stripe_full = os.getenv("STRIPE_PRICE_FULL")
        stripe_success = os.getenv("STRIPE_SUCCESS_URL")
        stripe_cancel = os.getenv("STRIPE_CANCEL_URL")
        public_url_env = os.getenv("DOCROPPER_PUBLIC_URL")
        lan_limit_env = os.getenv("DOCROPPER_LAN_USER_LIMIT")
        if env_key:
            merged["license_key"] = env_key
        if env_name:
            merged["license_name"] = env_name
        if google_id:
            merged["google_client_id"] = google_id
        if env_check is not None:
            merged["license_check"] = env_check.lower() == "true"
        if env_level:
            merged["license_level"] = env_level.lower()
        if dev_wm_env is not None:
            merged["developer_watermark"] = dev_wm_env.lower() == "true"
        if docuseal_url:
            merged["docuseal_api_url"] = docuseal_url
        if docuseal_key:
            merged["docuseal_api_key"] = docuseal_key
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

        # Apply values enforced by a previous license check
        overrides = load_license_overrides()
        if overrides:
            merged.update(overrides)

        dev_env = DEV_LICENSE_KEY_UPPER
        key_upper = merged.get("license_key", "").strip().upper()
        if key_upper == DEMO_FULL_LICENSE_KEY:
            merged["license_level"] = "full"
            merged["demo_full_mode"] = True
            if not merged.get("license_name"):
                merged["license_name"] = "Demo User"
            merged["enable_mobilesign"] = True
            if not merged.get("paypal_link"):
                merged["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
            if not merged.get("public_url"):
                merged["public_url"] = "https://doccropper.iltuoconsulenteit.it"
        elif (dev_env and key_upper == dev_env) or key_upper.endswith("-DEV"):
            merged["license_level"] = "full"
            if not merged.get("license_name"):
                merged["license_name"] = "Developer"
            merged["enable_mobilesign"] = True

        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()

def save_settings(update: dict):
    data = load_settings()
    overrides = load_license_overrides()
    filtered = {k: v for k, v in update.items() if k not in overrides}
    data.update(filtered)
    if os.getenv("DOCROPPER_PUBLIC_URL"):
        data["public_url"] = os.getenv("DOCROPPER_PUBLIC_URL")
    key_upper = data.get("license_key", "").strip().upper()
    dev_env = DEV_LICENSE_KEY_UPPER
    if key_upper == DEMO_FULL_LICENSE_KEY:
        data["license_level"] = "full"
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
        if not data.get("license_name"):
            data["license_name"] = "Developer"
        data["enable_mobilesign"] = True
    # Remove fields that are enforced by license
    license_locked = load_license_overrides()
    for key, val in license_locked.items():
        data[key] = val
    with open(SETTINGS_FILE, "w") as fh:
        json.dump(data, fh)
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

app = FastAPI()
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    from app.auth.database import engine, Base, async_session_maker
    from fastapi_users.db import SQLAlchemyUserDatabase
    from passlib.hash import bcrypt
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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

# Dependency used to enforce that the configured license is valid
async def require_valid_license(
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
):
    settings = load_settings()
    if not settings.get("license_check", False):
        return user

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.license_token:
        raise HTTPException(status_code=403, detail="Token licenza mancante")

    data = await verify_license(user.email, user.license_type, user.license_token)
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
app.mount("/js", NoCacheStaticFiles(directory="public/js"), name="js")
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

register_crop(app, plugin_utils)

settings = load_settings()
enable_sign = str(os.getenv('DOCROPPER_ENABLE_SIGN', settings.get('enable_sign', True))).lower() != 'false'
enable_mobilesign = str(os.getenv('DOCROPPER_ENABLE_MOBILESIGN', settings.get('enable_mobilesign', False))).lower() == 'true'
enable_remotesign = str(os.getenv('DOCROPPER_ENABLE_REMOTESIGN', settings.get('enable_remotesign', False))).lower() == 'true'
enable_removebg = str(os.getenv('DOCROPPER_ENABLE_REMOVEBG', settings.get('enable_removebg', False))).lower() == 'true'
enable_compresspdf = str(os.getenv('DOCROPPER_ENABLE_COMPRESSPDF', settings.get('enable_compresspdf', False))).lower() == 'true'

if enable_sign:
    register_sign(app, plugin_utils)
if enable_mobilesign:
    register_mobilesign(app, plugin_utils)
if enable_remotesign:
    register_remotesign(app, plugin_utils)
if enable_removebg:
    register_removebg(app, plugin_utils)
if enable_compresspdf and settings.get('license_level', 'free').lower() != 'free':
    register_compresspdf(app, plugin_utils)

@app.get("/me", tags=["auth"])
async def get_me(user: User = Depends(fastapi_users.current_user())):
    return {"email": user.email, "license": user.license_type}

@app.get('/favicon.ico')
async def favicon():
    icon_path = os.path.join(os.path.dirname(__file__), 'static', 'logos', 'app_logo.png')
    return FileResponse(icon_path, headers={"Cache-Control": "no-cache"})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
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
        lang = load_settings().get("language", "en")
        content = content.replace('<html lang="en">', f'<html lang="{lang}">')
        content = content.replace('</head>', f'<script>window.DC_LANG="{lang}";</script></head>')
        if CACHE_BUST:
            content = content.replace("styles.css", f"styles.css{CACHE_BUST}")
            content = content.replace("app.js", f"app.js{CACHE_BUST}")
            content = content.replace("mobilesign.js", f"mobilesign.js{CACHE_BUST}")
            content = content.replace("app_logo.png", f"app_logo.png{CACHE_BUST}")
            content = content.replace("header_logo.png", f"header_logo.png{CACHE_BUST}")
            content = content.replace("footer_logo.png", f"footer_logo.png{CACHE_BUST}")
            content = content.replace("DocCropper_slogan_en.png", f"DocCropper_slogan_en.png{CACHE_BUST}")
            content = content.replace("DocCropper_slogan_it.png", f"DocCropper_slogan_it.png{CACHE_BUST}")
    except FileNotFoundError:
        logger.error(f"{index_path} not found")
        return HTMLResponse(content="Frontend not found.", status_code=500)
    response = HTMLResponse(content=content, status_code=200)
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Pragma"] = "no-cache"
    response.set_cookie("session_id", session_id, httponly=True)
    return response


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
        if CACHE_BUST:
            content = content.replace("styles.css", f"styles.css{CACHE_BUST}")
            content = content.replace("admin.js", f"admin.js{CACHE_BUST}")
    except FileNotFoundError:
        return HTMLResponse(content="Admin page not found", status_code=404)
    return HTMLResponse(content=content, status_code=200)


@app.get("/settings/")
async def get_settings():
    data = load_settings()
    if not data.get("license_check") and not data.get("license_key"):
        data["license_key"] = "FREE"
        data["license_name"] = "Free Edition"
    data["version"] = VERSION
    data["version_date"] = VERSION_DATE
    if "stripe_secret_key" in data:
        data.pop("stripe_secret_key")
    return data


@app.post("/settings/")
async def update_settings(settings: dict = Body(...)):
    return save_settings(settings)


@app.get("/user-settings/")
async def get_user_settings_endpoint(request: Request):
    email = request.cookies.get("user_email")
    if not email:
        return JSONResponse(status_code=401, content={"message": "Not logged in"})
    data = load_user_settings(email)
    data["version"] = VERSION
    data["version_date"] = VERSION_DATE
    return data


@app.post("/user-settings/")
async def update_user_settings_endpoint(request: Request, settings: dict = Body(...)):
    email = request.cookies.get("user_email")
    if not email:
        return JSONResponse(status_code=401, content={"message": "Not logged in"})
    data = save_user_settings(email, settings)
    data["version"] = VERSION
    data["version_date"] = VERSION_DATE
    return data


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


@app.post("/google-login/")
async def google_login(token: str = Body(...)):
    settings = load_settings()
    client_id = settings.get("google_client_id", "")
    if not client_id:
        return JSONResponse(status_code=400, content={"message": "Google login not configured"})
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        resp = JSONResponse({"email": info.get("email"), "name": info.get("name")})
        if info.get("email"):
            resp.set_cookie("user_email", info.get("email"), httponly=True)
        return resp
    except Exception as e:
        logger.exception("Google token verification failed")
        return JSONResponse(status_code=400, content={"message": "Invalid token"})



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
        session_dir = get_session_dir(session_id)
        if session_dir:
            try:
                fname = os.path.join(session_dir, f"{uuid.uuid4().hex}.pdf{ENC_SUFFIX}")
                enc_pdf = encrypt_bytes(session_id, pdf_bytes)
                with open(fname, "wb") as fh:
                    fh.write(enc_pdf)
            except Exception:
                logger.exception("Failed to save uploaded PDF")

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
    pdfa: bool = Body(False),
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
        if pdfa:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                pdf_bytes = doc.tobytes(deflate=True, clean=True, garbage=4, pdfa=0)
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
        return JSONResponse(content={"pdf": "data:application/pdf;base64," + pdf_base64})
    except Exception as e:
        logger.exception("Failed to create PDF")
        return JSONResponse(status_code=500, content={"message": f"Could not create PDF: {str(e)}"})




@app.post("/ocr/")
async def extract_text(request: Request, images: list[str] = Body(...)):
    if pytesseract is None:
        return JSONResponse(status_code=503, content={"message": "OCR not available"})
    try:
        settings = load_settings()
        lang = settings.get("language", "en")
        text_parts = []
        for img_b64 in images:
            if img_b64.startswith('data:'):
                img_b64 = img_b64.split(',', 1)[1]
            img_bytes = base64.b64decode(img_b64)
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
