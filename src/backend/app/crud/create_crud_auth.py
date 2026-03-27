from datetime import datetime, timedelta
from typing import List, Union
from dotenv import load_dotenv
import os

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.schema_user import User
from ..validator import UserCreate

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Union[timedelta, None] = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # type: ignore


async def get_user(db: AsyncSession, username: str) -> Union[User, None]:
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Union[User, bool]:
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):  # type: ignore
        return False
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return False

    await db.delete(user)
    await db.commit()
    return True


async def get_all_users(db: AsyncSession) -> List[User]:
    query = select(User).order_by(User.id)
    result = await db.execute(query)
    return result.scalars().all()  # type: ignore


async def reset_user_password(
    db: AsyncSession, user_id: int, new_password: str
) -> bool:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        return False

    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password  # type: ignore
    await db.commit()
    await db.refresh(user)
    return True
