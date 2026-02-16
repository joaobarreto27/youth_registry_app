from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
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

    def initialize_engine(self) -> Engine:
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
            f"postgresql+psycopg2://{db_user}:{db_host}@{db_pass}:{db_port}/{db_name}"
        )
        return create_engine(url=connection_string)

    def connect(self, max_retries: int = 5, wait_seconds: int = 2) -> Engine | None:
        for attempt in range(1, max_retries + 1):
            try:
                self.engine: Engine = self.initialize_engine()

                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return self.engine

            except OperationalError as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")

                if attempt == max_retries:
                    raise Exception(
                        f"Unable to connect to the database after {max_retries} attempts"
                    )
                time.sleep(wait_seconds * attempt)

    def create_schema(self, max_retries: int = 5, wait_seconds: int = 5):
        if self.base is None:
            raise ValueError("The base model (declarative_base) was not provided.")

        if self.engine is None:
            self.connect()
            if self.engine is None:
                raise RuntimeError("Engine creation failed")

        for attempt in range(1, max_retries + 1):
            try:
                self.base.metadata.create_all(bind=self.engine)  # type: ignore
            except OperationalError as e:
                print(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt == max_retries:
                    raise ValueError(f"Failed to create schema: {e}")
                time.sleep(wait_seconds * attempt)
