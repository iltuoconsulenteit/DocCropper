from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Column, Integer, DateTime, ForeignKey, func
from app.auth.database import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    license_type = Column(String(length=10), default="free")
    license_token = Column(String(length=64), nullable=True)


class UserSession(Base):
    """Track active login sessions for each user."""

    __tablename__ = "user_session"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), index=True)
    token = Column(String(length=256), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
