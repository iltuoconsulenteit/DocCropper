import logging
from fastapi import Body
from fastapi.responses import JSONResponse

__all__ = ["register"]

logger = logging.getLogger(__name__)


def register(app, utils):
    load_settings = utils["load_settings"]

    @app.post("/google-login/")
    async def google_login(token: str = Body(...)):
        settings = load_settings()
        client_id = settings.get("google_client_id", "")
        if not client_id:
            return JSONResponse(status_code=400, content={"message": "Google login not configured"})
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests
            info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
            resp = JSONResponse({"email": info.get("email"), "name": info.get("name")})
            if info.get("email"):
                resp.set_cookie("user_email", info.get("email"), httponly=True)
            return resp
        except Exception:
            logger.exception("Google token verification failed")
            return JSONResponse(status_code=400, content={"message": "Invalid token"})
