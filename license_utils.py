import os

def get_dev_license_key() -> str:
    """Return the developer license key in uppercase."""
    return os.environ.get("DOCROPPER_DEV_LICENSE", "").strip().upper()
