"""DocCropper Django platform package.

This package shares its name with Python's :mod:`platform` standard
library module. To prevent runtime conflicts with dependencies that
expect the standard module, we load the real stdlib implementation and
re-export its public attributes here.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import sysconfig

# Locate and load the original stdlib ``platform`` module.
#
# When using the embeddable Windows distribution, the standard library may be
# packaged inside a ``pythonXY.zip`` archive rather than as loose ``.py`` files
# under ``Lib``.  The previous implementation expected ``platform.py`` to exist
# as a regular file, which caused a ``FileNotFoundError`` on such installs.
#
# To support both layouts we ask Python's ``PathFinder`` to resolve the module
# spec while restricting the search to known stdlib locations.  This works for
# directories and zip archives alike.
_stdlib_paths = []
_path = sysconfig.get_path("stdlib")
if _path:
    _stdlib_paths.append(_path)
_stdlib_paths.append(os.path.dirname(os.__file__))

_spec = None
for _p in _stdlib_paths:
    _spec = importlib.machinery.PathFinder.find_spec("platform", [_p])
    if _spec and _spec.loader:
        break
if _spec is None or _spec.loader is None:
    raise ModuleNotFoundError("Could not locate the standard library 'platform' module")

_stdlib_platform = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib_platform)

# Re-export the stdlib platform's public attributes so third-party imports
# continue to function as expected.
for _name in dir(_stdlib_platform):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del _name, _stdlib_platform, _spec, _stdlib_paths, _p, _path

