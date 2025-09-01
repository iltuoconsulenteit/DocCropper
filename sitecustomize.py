"""Startup tweaks applied to every Python process.

This module is imported automatically by Python if present on the path.
It patches third-party modules and performs small environment adjustments
needed by DocCropper.  By setting the process title here we make sure that
all helper scripts (Celery workers, management commands, etc.) show up with
an identifiable name instead of the generic ``python`` entry.
"""

import bcrypt
from types import SimpleNamespace

# Ensure Passlib can read the bcrypt version even on newer releases
if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = SimpleNamespace(__version__=getattr(bcrypt, "__version__", ""))

# Try to label the running process so it is easier to spot in task managers.
try:  # pragma: no cover - platform specific
    import setproctitle

    setproctitle.setproctitle("DocCropper")
except Exception:  # noqa: BLE001
    try:  # Fallback for Windows without setproctitle
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW("DocCropper")
    except Exception:  # noqa: BLE001
        pass

