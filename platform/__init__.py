"""DocCropper Django platform package.

This package shares its name with Python's :mod:`platform` standard
library module. To prevent runtime conflicts with dependencies that
expect the standard module, we load the real stdlib implementation and
re-export its public attributes here.
"""

from __future__ import annotations

import importlib.util
import os
import sysconfig

# Locate and load the original stdlib ``platform`` module
_stdlib_platform_path = os.path.join(sysconfig.get_path("stdlib"), "platform.py")
_spec = importlib.util.spec_from_file_location("_stdlib_platform", _stdlib_platform_path)
_stdlib_platform = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_stdlib_platform)

# Re-export the stdlib platform's public attributes so third-party imports
# continue to function as expected.
for _name in dir(_stdlib_platform):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del _name, _stdlib_platform, _spec, _stdlib_platform_path

