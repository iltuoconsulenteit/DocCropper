from sqlalchemy import Column, String, DateTime, Enum, JSON
from sqlalchemy.dialects.postgresql import ARRAY
import enum

from .database import Base


class LicenseType(str, enum.Enum):
    free = "free"
    demo = "demo"
    demo_full = "demo_full"
    developer = "developer"
    pro = "pro"


class License(Base):
    __tablename__ = "licenses"

    key = Column(String, primary_key=True, index=True)
    license_type = Column(Enum(LicenseType), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    allowed_domains = Column(ARRAY(String))
    plugins = Column(JSON)
    settings = Column(JSON)
