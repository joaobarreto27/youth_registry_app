from fastapi import FastAPI
from .engine_database import engine, Base
from .routes import router_register_members

engine = engine

api = FastAPI(
    title="Youth Registry API",
    description="Sistema de cadastro de membros",
    version="1.0.0",
)


@api.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:  # type: ignore
        await conn.run_sync(Base.metadata.create_all)


@api.get("/")
async def read_root():
    return {"status": "online", "message": "API is up and running"}


api.include_router(router_register_members, prefix="/registered", tags=["members"])
