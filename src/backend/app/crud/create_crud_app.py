from math import e
from pathlib import Path

from sqlalchemy.exc import IntegrityError

from ..engine_database import engine
from ..schemas import YouthMembersSchema
from ....utils import SqlReadFile
from ..validator import (
    YouthMemberCreate,
    YouthMemberResponse,
    YouthMembersBase,
    YouthMemberUpdate,
)


from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def create_member(
    db: AsyncSession, member: YouthMemberCreate, commit: bool = True
) -> YouthMemberResponse:

    if not member.member_name or len(member.member_name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do membro não pode estar vazio!",
        )

    if not member.phone_number or len(member.phone_number.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de telefone do membro não pode estar vazio!",
        )

    if member.t_shirt not in [
        "PP",
        "P",
        "M",
        "G",
        "GG",
        "XG",
        "EG",
        "G1",
        "G2",
        "G3",
        "G4",
    ]:
        raise HTTPException(
            status_code=400, detail="Número da camiseta não pode estar vazio!"
        )

    if member.food_allergy not in ["Sim", "Não"]:
        raise HTTPException(status_code=400, detail="Alergia não pode estar vazio!")

    if member.sower not in ["Sim", "Não"]:
        raise HTTPException(
            status_code=400, detail="Informacão de semeador não pode estar vazio"
        )

    if member.ministry_position not in ["Sim", "Não"]:
        raise HTTPException(
            status_code=400, detail="Informacão de semeador não pode estar vazio!"
        )

    if not member.date_birth:
        raise HTTPException(
            status_code=400, detail="Data de nascimento não pode estar vazia!"
        )

    if not member.email:
        raise HTTPException(status_code=400, detail="Email não pode estar vazio!")

    member = YouthMembersSchema(**member.model_dump())  # type: ignore

    try:
        if commit:
            db.add(member)
            await db.commit()
            await db.refresh(member)

        return member  # type: ignore
    except IntegrityError as e:
        if "pk_member_composite" in str(e.orig):
            await db.rollback()
            raise HTTPException(
                status_code=400, detail="Este membro já está cadastrado."
            )
        else:
            await db.rollback()
            raise e


async def delete_member(db: AsyncSession, id_member: int, commit: bool = True):
    current_dir = Path(__file__).parent

    validate_member = SqlReadFile(
        sql_file="validate_id_member", engine=engine, current_dir=current_dir
    ).read_sql_file()

    query = text(validate_member)
    result = await db.execute(query, {"id_member": id_member})
    result_query = result.mappings().first()

    if not result_query:
        raise HTTPException(status_code=404, detail="Membro não encontrado!")

    delete_query = SqlReadFile(
        sql_file="delete_member", engine=engine, current_dir=current_dir
    ).read_sql_file()
    await db.execute(text(delete_query), {"id_member": id_member})

    if commit:
        await db.commit()

    return {"detail": f"Jovem {id_member} removido do cadastro com sucesso"}


async def get_all_members(db: AsyncSession):
    all_members = SqlReadFile(
        sql_file="get_all_members", engine=engine, current_dir=Path(__file__).parent
    )
    all_members.read_sql_file()
    rows = await all_members.execute_query_sql()

    if not rows:
        raise HTTPException(status_code=404, detail="Não há membro cadastrados")

    return [YouthMemberResponse(**dict(row._mapping)) for row in rows]  # type: ignore


async def get_participant_by_id(db: AsyncSession, id_member: int):
    member_by_id = SqlReadFile(
        sql_file="get_member_by_id", engine=engine, current_dir=Path(__file__).parent
    ).read_sql_file()

    result = await db.execute(text(member_by_id), {"id_member": id_member})
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Registro de membro não encontrado")

    return YouthMemberResponse.model_validate(dict(row._mapping)).model_dump()


async def update_member(
    db: AsyncSession,
    id_member: int,
    member_update: YouthMemberUpdate,
    commit: bool = True,
):

    update_member_query = SqlReadFile(
        sql_file="update_member", engine=engine, current_dir=Path(__file__).parent
    ).read_sql_file()

    params = member_update.model_dump(exclude_none=True)

    if not params:
        raise HTTPException(status_code=400, detail="Escolha um campo para alterar")

    params = member_update.model_dump(exclude_unset=False)
    params["id_member"] = id_member
    result = await db.execute(text(update_member_query), params=params)

    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Membro não encontrado")

    try:
        if commit:
            await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Erro inesperado, tente novamente!")

    return YouthMemberResponse.model_validate(row).model_dump(exclude_none=True)
