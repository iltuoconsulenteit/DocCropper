"""Helpers for loading DocCropper plugins based on configuration."""

from __future__ import annotations

import logging
from typing import Iterable, Mapping, Sequence

from fastapi import FastAPI

from app.plugins.base import Plugin

logger = logging.getLogger(__name__)


async def load_plugins(
    app: FastAPI, utils: Mapping[str, object], plugins: Iterable[Plugin]
) -> list[Plugin]:
    """Load and register the provided plugins."""

    active: list[Plugin] = []
    for plugin in plugins:
        if hasattr(plugin, "enabled") and not getattr(plugin, "enabled"):
            logger.info("Skipping disabled plugin: %s", plugin.name)
            continue
        logger.info("Initializing plugin: %s", plugin.name)
        await plugin.on_init(app)
        plugin.register(app, utils)
        active.append(plugin)
    logger.info("Loaded %d plugins", len(active))
    return active


async def shutdown_plugins(app: FastAPI, plugins: Sequence[Plugin]) -> None:
    """Invoke shutdown hooks for loaded plugins."""

    for plugin in plugins:
        try:
            await plugin.on_shutdown(app)
        except Exception:
            logger.exception("Plugin shutdown hook failed: %s", plugin.name)

