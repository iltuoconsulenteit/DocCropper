from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import String, Column, Integer, DateTime
from app.auth.database import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    license_type = Column(String(length=10), default="free")
    license_token = Column(String(length=64), nullable=True)
    max_sessions = Column(Integer, nullable=True)
    subscription_id = Column(String(length=64), nullable=True)
    subscription_ends_at = Column(DateTime, nullable=True)
