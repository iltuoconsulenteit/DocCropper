from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Column, Integer, DateTime
from app.auth.database import Base
from datetime import datetime

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    license_type = Column(String(length=10), default="free")
    license_token = Column(String(length=64), nullable=True)


class UserSession(Base):
    """Track active user sessions."""

    __tablename__ = "user_session"
    session_id = Column(String(length=36), primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    last_active = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ip = Column(String(length=45), nullable=True)
