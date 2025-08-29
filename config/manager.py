import json
import logging
import os
import tempfile
from pathlib import Path
import subprocess

import bcrypt
from dotenv import load_dotenv
from license_utils import get_dev_license_key

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_FILE = BASE_DIR / "settings.json"
LICENSE_OVERRIDES_FILE = BASE_DIR / "license_overrides.json"
ENV_DIR = BASE_DIR / "env"

if ENV_DIR.is_dir():
    for name in sorted(os.listdir(ENV_DIR)):
        if name.endswith(".env"):
            load_dotenv(ENV_DIR / name, override=True)

DEFAULT_DEV_PASSWORD = os.getenv("DOCROPPER_DEV_PASSWORD", "87654321")
DEFAULT_SETTINGS_PASSWORD = os.getenv("DOCROPPER_SETTINGS_PASSWORD", "12345678")

DEMO_FULL_LICENSE_KEY = "DEMO-FULL-DC"
DEFAULT_SPONSOR_FRAME = (
    "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2F"
    "iltuoconsulenteit%3Flocale%3Dit_IT&tabs=timeline&width=340&height=500&small_header=true&"
    "adapt_container_width=true&hide_cover=true&show_facepile=false"
)

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
    VERSION = os.getenv("DOCROPPER_BUILD_VERSION", "unknown")
    VERSION_DATE = os.getenv("DOCROPPER_BUILD_DATE", "")

CACHE_BUST = f"?v={VERSION}"

DEFAULT_MAX_UPLOAD_MB = 5
MAX_UPLOAD_MB = int(os.getenv("DOCROPPER_MAX_UPLOAD_MB", str(DEFAULT_MAX_UPLOAD_MB)))
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024


def _bcrypt_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


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
    "developer_password_hash": None,
}

DEFAULT_SETTINGS["developer_password_hash"] = _bcrypt_hash(DEFAULT_DEV_PASSWORD)


def load_license_overrides() -> dict:
    if not LICENSE_OVERRIDES_FILE.exists():
        return {}
    try:
        with open(LICENSE_OVERRIDES_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}


def _atomic_write(path: Path, data: dict, indent: int | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh, indent=indent)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, path)
    finally:
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass


def save_license_overrides(update: dict) -> dict:
    data = load_license_overrides()
    data.update(update)
    _atomic_write(LICENSE_OVERRIDES_FILE, data)
    return data


def load_settings():
    if not SETTINGS_FILE.exists():
        _atomic_write(SETTINGS_FILE, DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE) as fh:
            base = json.load(fh)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(base)
        plugins_dir = BASE_DIR / "plugins"
        try:
            for name in os.listdir(plugins_dir):
                cfg_path = plugins_dir / name / "settings.json"
                if cfg_path.exists():
                    with open(cfg_path) as pf:
                        merged.update(json.load(pf))
        except Exception:
            pass
        max_mb_env = os.getenv("DOCROPPER_MAX_UPLOAD_MB")
        if max_mb_env:
            merged["max_upload_mb"] = int(max_mb_env)
        env_key = os.getenv("DOCROPPER_LICENSE_KEY")
        env_name = os.getenv("DOCROPPER_LICENSE_NAME")
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

        if not merged.get("developer_password_hash"):
            merged["developer_password_hash"] = _bcrypt_hash(DEFAULT_DEV_PASSWORD)
        if not merged.get("settings_password_hash"):
            merged["settings_password_hash"] = _bcrypt_hash(DEFAULT_SETTINGS_PASSWORD)

        overrides = load_license_overrides()
        if overrides:
            merged.update(overrides)

        dev_env = get_dev_license_key()
        key_upper = merged.get("license_key", "").strip().upper()
        is_demo = key_upper == DEMO_FULL_LICENSE_KEY
        is_dev = bool(dev_env) or key_upper.endswith("-DEV")
        if is_demo:
            merged["license_level"] = "full"
            merged["demo_full_mode"] = True
            if not merged.get("license_name"):
                merged["license_name"] = "Demo User"
            merged["enable_mobilesign"] = True
            if not merged.get("paypal_link"):
                merged["paypal_link"] = "https://www.paypal.com/donate/?hosted_button_id=XGKVRL2YQBPDY"
            if not merged.get("public_url"):
                merged["public_url"] = "https://doccropper.iltuoconsulenteit.it"
        elif is_dev:
            merged["license_level"] = "developer"
            if env_key:
                merged["license_key"] = env_key
            elif not merged.get("license_key") and dev_env:
                merged["license_key"] = dev_env
            if env_name:
                merged["license_name"] = env_name
            elif not merged.get("license_name"):
                merged["license_name"] = "Developer"
            merged["enable_mobilesign"] = True
            try:
                with open(SETTINGS_FILE) as fh:
                    current = json.load(fh)
            except Exception:
                current = {}
            desired = {
                "license_key": merged.get("license_key", ""),
                "license_name": merged.get("license_name", ""),
                "license_level": "developer",
            }
            if any(current.get(k) != v for k, v in desired.items()):
                current.update(desired)
                try:
                    _atomic_write(SETTINGS_FILE, current)
                except Exception:
                    pass
        if (is_demo or is_dev) and not merged.get("sponsor_frame"):
            merged["sponsor_frame"] = DEFAULT_SPONSOR_FRAME
        try:
            from plugins import sponsorframe
            sponsor_dev = str(os.getenv("DOCROPPER_SPONSORFRAME_DEV_ONLY", merged.get("sponsorframe_dev_only", False))).lower() == "true"
            if not sponsor_dev or is_dev:
                merged.update(sponsorframe.get_config(merged))
        except Exception:
            logger.exception("sponsor plugin failed")

        masked_key = key_upper[:4] + "..." if key_upper else "none"
        logger.info(
            "Loaded license %s (%s) - version %s (%s)",
            merged.get("license_level"),
            masked_key,
            VERSION,
            VERSION_DATE,
        )
        return merged
    except Exception:
        return DEFAULT_SETTINGS.copy()


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
        'imageeditor': ['enable_imageeditor', 'imageeditor_dev_only']
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
    dev_env = get_dev_license_key()
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
    elif bool(dev_env) or key_upper.endswith("-DEV"):
        data["license_level"] = "developer"
        if not data.get("license_name"):
            data["license_name"] = "Developer"
        data["enable_mobilesign"] = True
    license_locked = load_license_overrides()
    for key, val in license_locked.items():
        data[key] = val
    _atomic_write(SETTINGS_FILE, data)
    for pname, vals in plugin_updates.items():
        cfg_path = BASE_DIR / 'plugins' / pname / 'settings.json'
        current = {}
        if cfg_path.exists():
            try:
                with open(cfg_path) as fh:
                    current = json.load(fh)
            except Exception:
                pass
        current.update(vals)
        _atomic_write(cfg_path, current, indent=2)
    return data
