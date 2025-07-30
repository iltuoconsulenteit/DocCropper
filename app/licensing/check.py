import httpx
from fastapi import HTTPException
import os

async def verify_license(email: str, license_type: str) -> bool:
    license_url = os.getenv("LICENSE_CHECK_URL")
    if not license_url:
        return True  # fallback: passes when not configured

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(license_url, params={
                "email": email,
                "license": license_type
            })
            if response.status_code == 200:
                data = response.json()
                return data.get("valid", False)
            else:
                return False
    except Exception:
        raise HTTPException(status_code=500, detail="Errore durante la verifica della licenza")

