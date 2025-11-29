from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    JWTStrategy,
    AuthenticationBackend,
    CookieTransport,
)
from app.auth.models import User, UserSession
from app.auth.user_manager import UserManager
from app.auth.database import get_user_db, async_session_maker
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from sqlalchemy import delete, select, func
import os
from plugin.pocketbase_plugin import PocketBasePlugin, get_active_plugin

cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=3600)

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=os.getenv("SECRET_KEY"), lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

auth_router = fastapi_users.get_auth_router(auth_backend)
# Drop the default login and logout routes so we can manage session tracking
auth_router.routes = [
    r
    for r in auth_router.routes
    if not (
        (getattr(r, "path", "") == "/logout" and "POST" in getattr(r, "methods", []))
        or (getattr(r, "path", "") == "/login" and "POST" in getattr(r, "methods", []))
    )
]

router.include_router(
    auth_router,
    prefix="/auth/jwt",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


async def active_session_count(user_id: int) -> int:
    """Return the number of active sessions for the given user."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(func.count(UserSession.id)).where(UserSession.user_id == user_id)
        )
        return result.scalar() or 0


@router.post("/auth/jwt/login")
async def login(
    response: Response,
    credentials: OAuth2PasswordRequestForm = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
):
    pocketbase = get_active_plugin()
    if isinstance(pocketbase, PocketBasePlugin) and pocketbase.config.enabled:
        auth = pocketbase.authenticate(credentials.username, credentials.password)
        if not auth or not auth.get("token"):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = auth.get("token")
        record = auth.get("record", {})
        response.set_cookie(
            cookie_transport.cookie_name,
            token,
            max_age=cookie_transport.cookie_max_age,
            httponly=True,
            samesite="lax",
        )
        if record.get("email"):
            response.set_cookie("user_email", record.get("email"), httponly=True)
        pocketbase.track_session(record, token)
        return {"access_token": token, "token_type": "bearer", "backend": "pocketbase"}

    user = await user_manager.authenticate(credentials)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    count = await active_session_count(user.id)
    max_sessions = getattr(user, "max_sessions", 1)
    if count >= max_sessions:
        raise HTTPException(status_code=403, detail="Too many active sessions")

    token = await get_jwt_strategy().write_token(user)
    response.set_cookie(
        cookie_transport.cookie_name,
        token,
        max_age=cookie_transport.cookie_max_age,
        httponly=True,
        samesite="lax",
    )

    async with async_session_maker() as session:
        session.add(UserSession(user_id=user.id, token=token))
        await session.commit()

    await user_manager.on_after_login(user, None, response)

    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/jwt/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
):
    """Remove the active UserSession entry and clear the auth cookie."""

    pocketbase = get_active_plugin()
    if isinstance(pocketbase, PocketBasePlugin) and pocketbase.config.enabled:
        token = request.cookies.get(cookie_transport.cookie_name) or request.cookies.get("pocketbase_token")
        pocketbase.end_session(token)
        response.delete_cookie(cookie_transport.cookie_name)
        response.delete_cookie("user_email")
        return Response(status_code=204)

    token = request.cookies.get(cookie_transport.cookie_name)
    if user and token:
        async with async_session_maker() as session:
            await session.execute(
                delete(UserSession).where(
                    UserSession.user_id == user.id,
                    UserSession.token == token,
                )
            )
            await session.commit()

    response.delete_cookie(cookie_transport.cookie_name)
    return Response(status_code=204)
