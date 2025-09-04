import hashlib
import uuid


def get_machine_fingerprint() -> str:
    """Return a stable fingerprint for the current machine.

    Uses the MAC address provided by ``uuid.getnode`` and hashes it so the
    original hardware identifier is not exposed directly.
    """
    node = uuid.getnode()
    return hashlib.sha256(str(node).encode()).hexdigest()
