import os
import datetime
import httpx
from fastapi import HTTPException

async def verify_license(email: str, license_type: str, token: str) -> dict:
    """Check the remote Fabrik table and return the parsed response.

    The returned object always contains at least ``{"valid": bool}`` and may
    include a ``plugins`` map of optional components or a ``settings`` object
    with configuration values that should override the local ones.
    """

    license_url = os.getenv("LICENSE_CHECK_URL")
    if not license_url and license_type == "developer":
        license_url = "https://www.iltuoconsulenteit.it/site/index.php?option=com_fabrik&view=list&listid=XXX&format=raw"
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
                result = data if isinstance(data, dict) else {"valid": False}
            else:
                result = {"valid": False}
            log_line = (
                f"{datetime.datetime.utcnow().isoformat()} license check {license_type} {email} -> "
                f"{result.get('valid')}\n"
            )
            try:
                os.makedirs("temp", exist_ok=True)
                with open("temp/license_setup.log", "a") as log:
                    log.write(log_line)
            except Exception:
                pass
            return result
    except Exception:
        log_line = f"{datetime.datetime.utcnow().isoformat()} license check failed {license_type} {email}\n"
        try:
            os.makedirs("temp", exist_ok=True)
            with open("temp/license_setup.log", "a") as log:
                log.write(log_line)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Errore durante la verifica della licenza")
