from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./db.sqlite3")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db() -> None:
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_user_db():
    from fastapi_users.db import SQLAlchemyUserDatabase
    from app.auth.models import User
    async with async_session_maker() as session:
        yield SQLAlchemyUserDatabase(session, User)
