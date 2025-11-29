"""Base plugin interfaces used by DocCropper.

The plugin system is intentionally lightweight so optional features such as
authentication or database-backed routes can be disabled entirely. Plugins are
expected to register any FastAPI routes they need and optionally react to
startup/shutdown events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from fastapi import FastAPI


class Plugin(ABC):
    """Abstract base class for extensible DocCropper plugins."""

    name: str

    def __init__(self, name: str):
        self.name = name

    async def on_init(self, app: FastAPI) -> None:
        """Optional async hook executed during application startup."""

    @abstractmethod
    def register(self, app: FastAPI, utils: Mapping[str, Any]) -> None:
        """Register routes or other capabilities on the provided app."""

    async def on_shutdown(self, app: FastAPI) -> None:
        """Optional async hook executed during application shutdown."""


class FunctionPlugin(Plugin):
    """Adapter that wraps existing register functions in a Plugin interface."""

    def __init__(
        self,
        name: str,
        register_func,
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__(name)
        self.register_func = register_func
        self.enabled = enabled

    def register(self, app: FastAPI, utils: Mapping[str, Any]) -> None:  # type: ignore[override]
        if self.enabled:
            self.register_func(app, utils)

