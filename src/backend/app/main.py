from fastapi import FastAPI
from .engine_database import engine, Base
from .routes import router_register_members, router_auth
from dotenv import load_dotenv
import os

load_dotenv()
ENV = os.getenv("ENV_MODE", "PRD")

engine = engine

app = FastAPI(
    title="Youth Registry API",
    description="Sistema de cadastro de membros",
    version="1.0.0",
    docs_url="/docs" if ENV != "PRD" else None,
    redoc_url="/redoc" if ENV != "PRD" else None,
    openapi_url="/openapi.json" if ENV != "PRD" else None,
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:  # type: ignore
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def read_root():
    return {"status": "online", "message": "API is up and running"}


app.include_router(router_register_members, prefix="/registered", tags=["members"])


app.include_router(router_auth, prefix="/auth", tags=["authentication"])
