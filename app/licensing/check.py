import httpx
from fastapi import HTTPException
import os


async def verify_license(
    email: str,
    license_type: str,
    token: str,
    domain: str | None = None,
    fingerprint: str | None = None,
) -> dict:
    """Check the remote Fabrik table and return the parsed response.

    The returned object always contains at least ``{"valid": bool}`` and may
    include a ``plugins`` map of optional components or a ``settings`` object
    with configuration values that should override the local ones.  When
    ``domain`` or ``fingerprint`` are provided they are forwarded so the license
    server can enforce domain- or machine-scoped licenses.
    """

    license_url = os.getenv("LICENSE_CHECK_URL")
    if not license_url:
        return {"valid": True}  # fallback: passes when not configured

    try:
        async with httpx.AsyncClient() as client:
            params = {
                "email": email,
                "license": license_type,
                "token": token,
            }
            if domain:
                params["domain"] = domain
            if fingerprint:
                params["fingerprint"] = fingerprint
            response = await client.get(license_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, dict) else {"valid": False}
            return {"valid": False}
    except Exception:
        raise HTTPException(status_code=500, detail="Errore durante la verifica della licenza")

