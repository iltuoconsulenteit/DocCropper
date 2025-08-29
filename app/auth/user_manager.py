from fastapi_users import BaseUserManager, IntegerIDMixin
from app.auth.models import User
import os

SECRET = os.getenv("SECRET_KEY")

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    user_db_model = User
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
