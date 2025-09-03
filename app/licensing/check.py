import httpx
from fastapi import HTTPException
import os


async def verify_license(email: str, license_type: str, token: str) -> dict:
    """Check the remote license server and return the parsed response.

    The returned object always contains at least ``{"valid": bool}`` and may
    include optional metadata such as ``license_type`` and a list of
    ``features``.  Older servers may still return a ``plugins`` map or a
    ``settings`` object with configuration values that should override the
    local ones.
    """

    license_url = os.getenv("LICENSE_CHECK_URL")
    if not license_url:
        return {"valid": True}  # fallback: passes when not configured

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                license_url,
                params={
                    "email": email,
                    "license": license_type,
                    "token": token,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, dict) else {"valid": False}
            return {"valid": False}
    except Exception:
        raise HTTPException(status_code=500, detail="Errore durante la verifica della licenza")

