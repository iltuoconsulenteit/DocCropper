"""Sponsor frame plugin for DocCropper.

Provides dynamic sponsor content based on license settings. Supported modes:
- facebook: embed latest post from a Facebook page
- instagram: embed profile feed
- landing: generic iframe to a provided URL
- banner/image: show static image banner with optional link
- slide: rotate through multiple images
If `sponsor_plugin` is empty or "none" the sponsor frame is disabled.
"""
from __future__ import annotations

from typing import Dict, Any


def get_config(settings: Dict[str, Any]) -> Dict[str, Any]:
    """Return sponsor configuration based on settings.

    Parameters
    ----------
    settings: dict
        Loaded application settings.
    """
    mode = (settings.get("sponsor_plugin") or "").lower()
    if not mode or mode == "none":
        return {"sponsor_frame": "", "sponsor_banner": "", "sponsor_slides": []}

    cfg: Dict[str, Any] = {}
    url = settings.get("sponsor_url", "")

    if mode == "facebook":
        page = settings.get("sponsor_facebook_page", "iltuoconsulenteit")
        width = settings.get("sponsor_frame_width", 340)
        height = settings.get("sponsor_frame_height", 500)
        cfg["sponsor_frame"] = (
            "https://www.facebook.com/plugins/page.php?href="
            f"https://www.facebook.com/{page}&tabs=timeline&width={width}&height={height}"
            "&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=true"
        )
    elif mode == "instagram":
        profile = settings.get("sponsor_instagram_profile", "")
        if profile:
            cfg["sponsor_frame"] = f"https://www.instagram.com/{profile}/embed"
    elif mode == "landing":
        if url:
            cfg["sponsor_frame"] = url
    elif mode in {"banner", "image"}:
        banner = settings.get("sponsor_banner")
        if banner:
            cfg["sponsor_banner"] = banner
            if url:
                cfg["sponsor_url"] = url
    elif mode == "slide":
        slides = settings.get("sponsor_slides", [])
        if slides:
            cfg["sponsor_slides"] = slides
            if url:
                cfg["sponsor_url"] = url
    return cfg
