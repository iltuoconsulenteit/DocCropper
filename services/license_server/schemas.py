from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, EmailStr

from .models import LicenseType


class LicenseBase(BaseModel):
    key: str
    license_type: LicenseType
    expires_at: Optional[datetime]
    allowed_domains: List[str] = []
    plugins: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class LicenseCreate(BaseModel):
    email: EmailStr
    license_type: LicenseType
    expires_at: Optional[datetime] = None
    allowed_domains: List[str] = []
    plugins: Optional[Dict[str, Any]] = None
    settings: Optional[Dict[str, Any]] = None


class LicenseResponse(LicenseBase):
    class Config:
        orm_mode = True


class LicenseVerifyResponse(BaseModel):
    valid: bool
    license: Optional[LicenseResponse]
