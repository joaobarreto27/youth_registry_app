from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.exc import OperationalError
import time
import os
from typing import Optional
from dotenv import load_dotenv


class ConnectionDatabase:
    def __init__(self, base: Optional[object] = None) -> None:
        self.base: object | None = base
        self.sgbd_name: str = "postgres"
        self.engine = None  # type: ignore

        load_dotenv()

    def initialize_engine(self) -> AsyncEngine:
        db_host: str | None = os.getenv("DB_HOST")
        db_port: str | None = os.getenv("DB_PORT")
        db_user: str | None = os.getenv("DB_USER")
        db_pass: str | None = os.getenv("DB_PASSWORD")
        db_name: str | None = os.getenv("DB_NAME")

        if not all([db_user, db_pass, db_name, db_host, db_port]):
            raise ValueError(
                "Required variables are missing in the .env file: "
                "DB_USER, DB_PASSWORD, DB_NAME, DB_HOST and DB_PORT are required"
            )

        connection_string: str = (
            f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        )
        return create_async_engine(url=connection_string)

    def connect(
        self, max_retries: int = 5, wait_seconds: int = 2
    ) -> AsyncEngine | None:
        for attempt in range(1, max_retries + 1):
            try:
                self.engine: AsyncEngine = self.initialize_engine()
                return self.engine

            except OperationalError as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")

                if attempt == max_retries:
                    raise Exception(
                        f"Unable to create async engine after {max_retries} attempts"
                    )
                time.sleep(wait_seconds * attempt)

    async def create_schema(self, max_retries: int = 5, wait_seconds: int = 5):
        if self.base is None:
            raise ValueError("The base model (declarative_base) was not provided.")

        if self.engine is None:
            self.connect()
            if self.engine is None:
                raise RuntimeError("Engine creation failed")

        for attempt in range(1, max_retries + 1):
            try:
                async with self.engine.begin() as conn:  # type: ignore
                    await conn.run_sync(self.base.metadata.create_all)  # type: ignore
            except OperationalError as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt == max_retries:
                    raise ValueError(f"Failed to create schema: {e}")
                time.sleep(wait_seconds * attempt)
