"""DocCropper Django platform package.

This package shares its name with Python's :mod:`platform` standard
library module. To prevent runtime conflicts with dependencies that
expect the standard module, we load the real stdlib implementation and
re-export its public attributes here.
"""

from __future__ import annotations

import importlib
import os
import sys
import sysconfig

# Locate and load the original stdlib ``platform`` module.
#
# Embeddable Windows distributions often package the standard library inside a
# ``pythonXY.zip`` archive rather than as loose ``.py`` files.  Previous
# implementations attempted to load ``Lib/platform.py`` directly, which fails on
# such installs.  To support both layouts we temporarily prepend common stdlib
# locations to ``sys.path`` and import the real module via the regular import
# machinery.  This handles directories and zip archives transparently.

# Candidate search paths: the configured stdlib path, the interpreter directory
# and any ``python*.zip`` archives located there.
_stdlib_paths: list[str] = []
_path = sysconfig.get_path("stdlib")
if _path and os.path.isdir(_path):
    _stdlib_paths.append(_path)
_base = os.path.dirname(sys.executable)
_stdlib_paths.append(_base)
for _name in os.listdir(_base):
    if _name.lower().startswith("python") and _name.lower().endswith(".zip"):
        _stdlib_paths.insert(0, os.path.join(_base, _name))

# Import the real stdlib module while our package is temporarily removed from
# ``sys.modules`` so the import system doesn't resolve back to this file.
_saved_module = sys.modules.pop(__name__, None)
_saved_path = list(sys.path)
for _p in reversed(_stdlib_paths):
    if os.path.exists(_p):
        sys.path.insert(0, _p)
try:
    _stdlib_platform = importlib.import_module(__name__)
finally:
    sys.path[:] = _saved_path
    sys.modules[__name__] = _saved_module

# Re-export the stdlib platform's public attributes so third-party imports
# continue to function as expected.
for _name in dir(_stdlib_platform):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del (
    _stdlib_platform,
    _stdlib_paths,
    _path,
    _base,
    _saved_module,
    _saved_path,
)

