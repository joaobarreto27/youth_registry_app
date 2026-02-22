from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from ....utils import ConnectionDatabase
from .base import Base

connection = ConnectionDatabase(base=Base)
engine = connection.connect()

SessionLocal: sessionmaker[AsyncSession] = sessionmaker(  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
    bind=engine,  # type: ignore
)  # type: ignore


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
