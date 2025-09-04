from fastapi import APIRouter, Depends, Request, Response
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
from sqlalchemy import delete
import os

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
# Drop the default logout route so we can manage session cleanup manually
auth_router.routes = [
    r
    for r in auth_router.routes
    if not (getattr(r, "path", "") == "/logout" and "POST" in getattr(r, "methods", []))
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


@router.post("/auth/jwt/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    user: User | None = Depends(fastapi_users.current_user(optional=True)),
):
    """Remove the active UserSession entry and clear the auth cookie."""

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
