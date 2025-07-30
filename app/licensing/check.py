import httpx
from fastapi import HTTPException
import os


async def verify_license(email: str, license_type: str, token: str) -> dict:
    """Check the remote Fabrik table and return the parsed response.

    The returned object always contains at least ``{"valid": bool}`` and may
    optionally include a ``plugins`` mapping of enabled components.
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

