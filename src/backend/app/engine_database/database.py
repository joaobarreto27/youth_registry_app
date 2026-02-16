from typing import Any, Generator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from ....utils import ConnectionDatabase
from ..schemas import Base, YouthMembersSchema  # noqa: F401


connection = ConnectionDatabase(base=Base)
engine = connection.connect()
connection.create_schema()

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def get_db(self) -> Generator[Session, Any, None]:
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
