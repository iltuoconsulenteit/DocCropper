"""DocCropper Django platform package.

This package shares its name with Python's :mod:`platform` standard
library module. To prevent runtime conflicts with dependencies that
expect the standard module, we load the real stdlib implementation and
re-export its public attributes here.
"""

from __future__ import annotations

import importlib
import importlib.machinery as _mach
import importlib.util as _util
import os
import sys
import sysconfig
import zipimport

# Locate and load the original stdlib ``platform`` module.
#
# Embeddable Windows distributions often package the standard library inside a
# ``pythonXY.zip`` archive rather than as loose ``.py`` files. Previous
# implementations attempted to prepend candidate paths to ``sys.path`` and rely
# on ``importlib.import_module``. On some installations this still resolved to
# the local project package or a missing ``Lib`` directory.  Instead we search
# explicit locations using ``PathFinder`` so directories and zip archives are
# handled uniformly without touching ``sys.path``.

# Candidate search paths: configured stdlib directory (if any), the interpreter
# directory, and any sibling ``python*.zip`` archives.
_search_paths: list[str] = []
_path = sysconfig.get_path("stdlib")
if _path:
    _search_paths.append(_path)
_base = os.path.dirname(sys.executable)
_search_paths.append(_base)
for _name in os.listdir(_base):
    if _name.lower().startswith("python") and _name.lower().endswith(".zip"):
        _search_paths.insert(0, os.path.join(_base, _name))

_stdlib_platform = None
_spec = None
for _p in _search_paths:
    try:
        if os.path.isfile(_p) and _p.lower().endswith('.zip'):
            _stdlib_platform = zipimport.zipimporter(_p).load_module(__name__)
            break
        _spec = _mach.PathFinder.find_spec(__name__, [_p])
        if _spec and _spec.loader:
            _stdlib_platform = _util.module_from_spec(_spec)
            _spec.loader.exec_module(_stdlib_platform)
            break
    except Exception:
        pass
if _stdlib_platform is None:
    raise ModuleNotFoundError("Could not locate the standard library 'platform' module")

# Re-export the stdlib platform's public attributes so third-party imports
# continue to function as expected.
for _name in dir(_stdlib_platform):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del (
    _stdlib_platform,
    _search_paths,
    _spec,
    _path,
    _base,
)

