"""PocketBase integration helpers and routes.

This plugin provides a lightweight HTTP client for PocketBase so the
application can authenticate users and persist settings against a remote
PocketBase instance. It keeps the API surface close to the existing
helpers in :mod:`services.api.app`, falling back to local behavior when
the plugin is disabled or misconfigured.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

__all__ = ["PocketBasePlugin", "get_active_plugin", "register"]

logger = logging.getLogger(__name__)


@dataclass
class PocketBaseConfig:
    """Runtime configuration derived from ``settings.json``."""

    enabled: bool = False
    url: str = "http://127.0.0.1:8090"
    admin_token: str = ""
    collections: Dict[str, str] = field(
        default_factory=lambda: {
            "users": "users",
            "sessions": "sessions",
            "user_settings": "user_settings",
            "data": "data",
        }
    )

    @classmethod
    def from_settings(cls, settings: Dict[str, Any]) -> "PocketBaseConfig":
        return cls(
            enabled=bool(settings.get("enable_pocketbase_plugin", False)),
            url=settings.get("pocketbase_url") or "http://127.0.0.1:8090",
            admin_token=settings.get("pocketbase_admin_token", ""),
            collections={
                "users": settings.get("pocketbase_collections", {}).get("users", "users"),
                "sessions": settings.get("pocketbase_collections", {}).get(
                    "sessions", "sessions"
                ),
                "user_settings": settings.get("pocketbase_collections", {}).get(
                    "user_settings", "user_settings"
                ),
                "data": settings.get("pocketbase_collections", {}).get("data", "data"),
            },
        )


class PocketBasePlugin:
    """Wrapper around the PocketBase REST API with convenient helpers."""

    def __init__(self, config: PocketBaseConfig):
        self.config = config
        self._client = httpx.Client(base_url=self.config.url, timeout=10.0)

    # ---------- Internal HTTP helpers ----------
    def _headers(self, token: Optional[str] = None, use_admin: bool = False) -> dict:
        headers: dict[str, str] = {}
        auth_token = token
        if use_admin and self.config.admin_token:
            auth_token = self.config.admin_token
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        use_admin: bool = False,
        **kwargs,
    ) -> dict | None:
        try:
            resp = self._client.request(
                method,
                path,
                headers=self._headers(token=token, use_admin=use_admin),
                **kwargs,
            )
            resp.raise_for_status()
            if resp.text:
                return resp.json()
            return {}
        except Exception:
            logger.exception("PocketBase request failed: %s %s", method, path)
            return None

    # ---------- Authentication helpers ----------
    def authenticate(self, identity: str, password: str) -> dict | None:
        """Authenticate a user via PocketBase.

        Returns the PocketBase auth response (token + record) or ``None`` on
        failure. Uses the configured ``users`` collection.
        """

        return self._request(
            "POST",
            f"/api/collections/{self.config.collections['users']}/auth-with-password",
            json={"identity": identity, "password": password},
        )

    def track_session(self, record: dict, token: str) -> None:
        """Persist a session token in the configured ``sessions`` collection."""

        collection = self.config.collections.get("sessions")
        if not collection or not token or not record:
            return
        payload = {
            "user": record.get("id"),
            "email": record.get("email"),
            "token": token,
        }
        self._request(
            "POST",
            f"/api/collections/{collection}/records",
            json=payload,
            use_admin=True,
        )

    def end_session(self, token: str | None) -> None:
        """Remove a stored session entry when logging out."""

        collection = self.config.collections.get("sessions")
        if not collection or not token:
            return
        data = self._request(
            "GET",
            f"/api/collections/{collection}/records",
            params={"filter": f"token='{token}'", "perPage": 1},
            use_admin=True,
        )
        if not data or not data.get("items"):
            return
        record_id = data["items"][0].get("id")
        if record_id:
            self._request(
                "DELETE",
                f"/api/collections/{collection}/records/{record_id}",
                use_admin=True,
            )

    # ---------- Settings helpers ----------
    def load_user_settings(self, email: str) -> dict | None:
        """Fetch stored settings for the given user."""

        collection = self.config.collections.get("user_settings")
        if not collection or not email:
            return None
        data = self._request(
            "GET",
            f"/api/collections/{collection}/records",
            params={"filter": f"email='{email}'", "perPage": 1},
            use_admin=True,
        )
        if not data or not data.get("items"):
            return None
        record = data["items"][0]
        payload = record.get("data") or {}
        if not isinstance(payload, dict):
            return None
        return payload

    def save_user_settings(self, email: str, update: dict) -> dict | None:
        """Persist user settings, creating the record if necessary."""

        collection = self.config.collections.get("user_settings")
        if not collection or not email:
            return None
        existing = self._request(
            "GET",
            f"/api/collections/{collection}/records",
            params={"filter": f"email='{email}'", "perPage": 1},
            use_admin=True,
        )
        if existing and existing.get("items"):
            record_id = existing["items"][0].get("id")
            payload = existing["items"][0].get("data") or {}
            if not isinstance(payload, dict):
                payload = {}
            payload.update(update or {})
            result = self._request(
                "PATCH",
                f"/api/collections/{collection}/records/{record_id}",
                json={"data": payload},
                use_admin=True,
            )
            return result.get("data") if isinstance(result, dict) else payload

        result = self._request(
            "POST",
            f"/api/collections/{collection}/records",
            json={"email": email, "data": update},
            use_admin=True,
        )
        if isinstance(result, dict):
            return result.get("data") or update
        return update

    # ---------- Generic CRUD wrappers ----------
    def list_records(self, collection: str, params: Optional[dict] = None) -> dict | None:
        return self._request(
            "GET",
            f"/api/collections/{collection}/records",
            params=params or {},
            use_admin=True,
        )

    def create_record(self, collection: str, payload: dict) -> dict | None:
        return self._request(
            "POST",
            f"/api/collections/{collection}/records",
            json=payload,
            use_admin=True,
        )

    def update_record(self, collection: str, record_id: str, payload: dict) -> dict | None:
        return self._request(
            "PATCH",
            f"/api/collections/{collection}/records/{record_id}",
            json=payload,
            use_admin=True,
        )

    def delete_record(self, collection: str, record_id: str) -> bool:
        result = self._request(
            "DELETE",
            f"/api/collections/{collection}/records/{record_id}",
            use_admin=True,
        )
        return result is not None


_ACTIVE_PLUGIN: PocketBasePlugin | None = None


def get_active_plugin() -> PocketBasePlugin | None:
    return _ACTIVE_PLUGIN


def register(app, utils: dict[str, Any]) -> PocketBasePlugin:
    """Configure PocketBase support and expose helper routes."""

    global _ACTIVE_PLUGIN
    config = PocketBaseConfig.from_settings(utils["load_settings"]())
    plugin = PocketBasePlugin(config)
    _ACTIVE_PLUGIN = plugin

    router = APIRouter(prefix="/auth/pocketbase", tags=["pocketbase"])

    @router.post("/login")
    async def pb_login(
        response: Response, credentials: OAuth2PasswordRequestForm = Depends()
    ):
        if not plugin.config.enabled:
            raise HTTPException(status_code=503, detail="PocketBase plugin disabled")
        auth = plugin.authenticate(credentials.username, credentials.password)
        if not auth or not auth.get("token"):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = auth.get("token")
        record = auth.get("record", {})
        plugin.track_session(record, token)
        if record.get("email"):
            response.set_cookie("user_email", record.get("email"), httponly=True)
        response.set_cookie("pocketbase_token", token, httponly=True)
        return {"access_token": token, "user": record}

    @router.post("/logout", status_code=204)
    async def pb_logout(request: Request, response: Response):
        token = request.cookies.get("pocketbase_token")
        plugin.end_session(token)
        response.delete_cookie("pocketbase_token")
        response.delete_cookie("user_email")
        return Response(status_code=204)

    app.include_router(router)
    app.state.pocketbase_plugin = plugin
    return plugin
