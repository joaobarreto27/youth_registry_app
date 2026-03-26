from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..engine_database import get_db
from ..schemas import User
from ..validator import UserCreate, UserResponse
from ..crud.create_crud_auth import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    get_user,
    create_user,
    delete_user,
    get_all_users,
)

router_auth = APIRouter()


@router_auth.post("/register", response_model=UserResponse)
async def register_endpoint(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    existing = await get_user(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Usuário já existe!")

    new_user = await create_user(db, user)
    return new_user  # type: ignore


@router_auth.post("/login")
async def login_endpoint(
    from_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    user = await authenticate_user(db, from_data.username, from_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
        )

    access_token = create_access_token(
        data={"sub": user.username},  # type: ignore
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router_auth.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int = Path(..., description="ID do usuário a ser removido"),
    db: AsyncSession = Depends(get_db),
):
    success = await delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )
    return None


@router_auth.get("/", response_model=List[UserResponse])
async def get_all_users_endpoint(
    db: AsyncSession = Depends(get_db),
) -> List[UserResponse]:
    users = await get_all_users(db)
    return users
