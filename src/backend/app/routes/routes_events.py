from typing import Dict, List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from ..engine_database import get_db, SessionLocal
from ..validator import YouthMemberCreate, YouthMemberResponse, YouthMemberUpdate
from ..crud import (
    create_member,
    delete_member,
    get_all_members,
    get_member_by_id,
    update_member,
)

router_register_members = APIRouter()


@router_register_members.get("/", response_model=List[YouthMemberResponse])
async def get_all_members_endpoint(db: AsyncSession = Depends(get_db)):
    return await get_all_members(db)


@router_register_members.post("/", response_model=YouthMemberResponse)
async def create_member_endpoint(
    member: YouthMemberCreate, db: AsyncSession = Depends(get_db)
):
    return create_member(db, member)


@router_register_members.get("/{id_member}", response_model=YouthMemberResponse)
async def get_member_by_id_endpoint(id_member, db: AsyncSession = Depends(get_db)):
    return await get_member_by_id(db, id_member)


@router_register_members.put("/{id_member}", response_model=YouthMemberResponse)
async def update_member_endpoint(
    id_member,
    member_update: YouthMemberUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_member(db, id_member, member_update)


@router_register_members.delete("/{id_member}")
async def delete_member_endpoint(id_member, db: AsyncSession = Depends(get_db)):
    return await delete_member(db, id_member)
