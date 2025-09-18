"""DocCropper Django platform package.

This package shares its name with Python's :mod:`platform` standard
library module. To prevent runtime conflicts with dependencies that
expect the standard module, we load the real stdlib implementation and
re-export its public attributes here.
"""

from __future__ import annotations

import importlib.machinery as _mach
import importlib.util as _util
import os
import sys
import sysconfig
import types as _types
import zipimport as _zipimport

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
try:
    for _name in os.listdir(_base):
        if _name.lower().startswith("python") and _name.lower().endswith(".zip"):
            _search_paths.insert(0, os.path.join(_base, _name))
except FileNotFoundError:
    pass


def _load_from_zip(path: str):
    """Attempt to load the stdlib ``platform`` module from a zip archive."""

    try:
        importer = _zipimport.zipimporter(path)
    except _zipimport.ZipImportError:
        return None

    try:
        code = importer.get_code(__name__)
    except ImportError:
        return None

    spec = _util.spec_from_loader(__name__, importer)
    module = _util.module_from_spec(spec) if spec else _types.ModuleType(__name__)
    # ``module_from_spec`` already assigns ``__loader__``/``__spec__`` when a
    # spec is provided.  When ``spec`` is ``None`` we set the key attributes
    # manually so the shim still resembles a normal module.
    module.__loader__ = importer
    module.__file__ = importer.get_filename(__name__)
    module.__package__ = ""
    exec(code, module.__dict__)
    return module

_stdlib_platform = None
for _p in _search_paths:
    try:
        if not _p:
            continue
        if _p.lower().endswith(".zip"):
            _stdlib_platform = _load_from_zip(_p)
        else:
            _spec = _mach.PathFinder.find_spec(__name__, [_p])
            if _spec and _spec.loader:
                # Some embeddable distributions advertise a ``Lib`` directory that
                # doesn't actually contain the standard library. Loading such specs
                # will raise ``FileNotFoundError``; in that case, continue searching
                # other candidate locations.
                try:
                    _stdlib_platform = _util.module_from_spec(_spec)
                    _spec.loader.exec_module(_stdlib_platform)
                except FileNotFoundError:
                    _stdlib_platform = None
                    continue
        if _stdlib_platform:
            break
    except Exception:
        _stdlib_platform = None
if _stdlib_platform is None:
    raise ModuleNotFoundError(
        "Could not locate the standard library 'platform' module"
    )

# Re-export the stdlib platform's public attributes so third-party imports
# continue to function as expected.
for _name in dir(_stdlib_platform):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_stdlib_platform, _name)

del (
    _stdlib_platform,
    _search_paths,
    _path,
    _base,
)

