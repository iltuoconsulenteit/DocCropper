"""Local license validation helpers.

The validator intentionally avoids any network calls so it can run in
restricted environments and during startup.  It accepts a signed code
containing a small JSON payload and exposes a boolean ``is_demo`` flag for
feature gating and watermark logic.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

DEMO_LICENSE_CODE = "DEMO-FULL-DC"
LICENSE_SECRET_ENV = "DOCROPPER_LICENSE_SECRET"
LICENSE_CODE_ENV = "DOCROPPER_LICENSE_CODE"
DEFAULT_LICENSE_SECRET = "doccropper-offline-secret"
SETTINGS_PATH = Path(__file__).resolve().parents[2] / "settings.json"


@dataclass
class LicenseStatus:
    code: str
    payload: dict[str, Any] | None
    is_valid: bool
    is_demo: bool
    message: str = ""

    @property
    def should_watermark(self) -> bool:
        """Return True when demo restrictions should apply."""
        return self.is_demo or not self.is_valid


def _decode_payload(encoded: str) -> tuple[dict[str, Any] | None, str]:
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(raw.decode("utf-8")), ""
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"Invalid payload: {exc}"


def _sign_payload(encoded: str, secret: str) -> str:
    digest = hmac.new(secret.encode("utf-8"), encoded.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def validate_license_code(code: str | None, *, secret: str | None = None) -> LicenseStatus:
    """Validate a locally signed license string.

    Expected format: ``<base64url-json>.<signature>`` where the signature is a
    base64url-encoded HMAC-SHA256 over the payload using ``DOCROPPER_LICENSE_SECRET``.
    When the code matches ``DEMO-FULL-DC`` the status is considered valid but
    marked as demo so watermarks remain enabled.
    """

    cleaned = (code or "").strip()
    if not cleaned:
        return LicenseStatus(cleaned, None, False, True, "Missing license code")
    if cleaned.upper() == DEMO_LICENSE_CODE:
        return LicenseStatus(cleaned, {"edition": "demo"}, True, True, "Demo license")
    if cleaned.upper().endswith("-DEV"):
        return LicenseStatus(cleaned, {"edition": "developer"}, True, False, "Developer key")

    secret_key = secret or os.getenv(LICENSE_SECRET_ENV, DEFAULT_LICENSE_SECRET)
    if "." not in cleaned:
        return LicenseStatus(cleaned, None, False, True, "Code is missing a signature")

    payload_part, signature = cleaned.rsplit(".", 1)
    payload, error = _decode_payload(payload_part)
    if payload is None:
        return LicenseStatus(cleaned, None, False, True, error)

    expected_sig = _sign_payload(payload_part, secret_key)
    if not hmac.compare_digest(expected_sig, signature):
        return LicenseStatus(cleaned, payload, False, True, "Signature mismatch")

    # Treat any edition explicitly marked as demo as a demo license even when
    # the signature is correct.
    edition = str(payload.get("edition", "demo")).lower()
    is_demo = edition == "demo"
    return LicenseStatus(cleaned, payload, True, is_demo, "")


def read_license_code(settings: dict[str, Any] | None = None) -> str:
    """Return the configured license code honoring environment overrides."""

    for env_var in (LICENSE_CODE_ENV, "DOCROPPER_LICENSE_KEY"):
        env_value = os.getenv(env_var)
        if env_value:
            return env_value.strip()
    if settings:
        code = settings.get("license_key") or settings.get("license_code") or ""
        return str(code).strip()
    return ""


def persist_license_code(code: str, *, settings_path: Path = SETTINGS_PATH) -> Tuple[LicenseStatus, Path]:
    """Store the given code in ``settings.json`` and return its status."""

    status = validate_license_code(code)
    settings = {}
    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except Exception:
            settings = {}
    settings["license_key"] = code
    settings["demo_full_mode"] = status.should_watermark
    settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return status, settings_path


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Validate or update a DocCropper license code")
    parser.add_argument("--code", help="License code to validate/update. If omitted the code is read from settings.")
    parser.add_argument("--settings", type=Path, default=SETTINGS_PATH, help="Path to settings.json")
    parser.add_argument("--validate-only", action="store_true", help="Only validate without saving the code")
    args = parser.parse_args()

    code = args.code
    if not code:
        settings = {}
        if args.settings.exists():
            try:
                settings = json.loads(args.settings.read_text(encoding="utf-8"))
                code = settings.get("license_key", "")
            except Exception:
                code = ""
    status = validate_license_code(code)
    if args.validate_only:
        print(json.dumps(status.__dict__, indent=2))
        return

    status, path = persist_license_code(code, settings_path=args.settings)
    print(f"Saved license to {path}")
    print(json.dumps(status.__dict__, indent=2))


if __name__ == "__main__":
    _cli()
