from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from ....utils import ConnectionDatabase
from ..schemas import Base, YouthMembersSchema  # noqa: F401


connection = ConnectionDatabase(base=Base)
engine = connection.connect()

SessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=engine
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
