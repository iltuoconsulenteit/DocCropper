from fastapi_users import schemas
from typing import Optional

class UserRead(schemas.BaseUser[int]):
    license_type: str
    license_token: Optional[str] = None

class UserCreate(schemas.BaseUserCreate):
    license_type: str = "free"
    license_token: Optional[str] = None

class UserUpdate(schemas.BaseUserUpdate):
    license_type: Optional[str] = None
    license_token: Optional[str] = None
