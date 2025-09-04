from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    JWTStrategy,
    AuthenticationBackend,
    CookieTransport,
)
from fastapi_users.jwt import generate_jwt
from app.auth.models import User
from app.auth.user_manager import UserManager
from app.auth.database import get_user_db
from app.auth.schemas import UserRead, UserCreate, UserUpdate
import os

cookie_transport = CookieTransport(cookie_name="auth", cookie_max_age=3600)


class CustomJWTStrategy(JWTStrategy):
    async def write_token(self, user):  # type: ignore[override]
        data = {"sub": str(user.id)}
        if self.token_audience is not None:
            data["aud"] = self.token_audience
        max_sessions = getattr(user, "max_sessions", None)
        if max_sessions is not None:
            data["max_sessions"] = max_sessions
        email = getattr(user, "email", None)
        if email is not None:
            data["email"] = email
        return generate_jwt(
            data,
            self.lifetime_seconds,
            self.secret,
            self.algorithm,
        )

def get_jwt_strategy() -> JWTStrategy:
    return CustomJWTStrategy(secret=os.getenv("SECRET_KEY"), lifetime_seconds=3600)

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
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
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
