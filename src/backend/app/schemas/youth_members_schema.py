from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, CHAR, DateTime
from sqlalchemy.sql import func

from . import Base


class YouthMembersSchema(Base):
    __tablename__: str = "youth_members"

    id_member: Column[int] = Column(Integer, primary_key=True, index=True)
    member_name: Column[str] = Column(String(255), nullable=False)
    phone_number: Column[str] = Column(String(15), nullable=False)
    t_shirt: Column[str] = Column(CHAR(2), nullable=False)
    food_allergy: Column[str] = Column(CHAR(3), nullable=False)
    sower: Column[str] = Column(CHAR(3), nullable=False)
    ministry_position: Column[str] = Column(CHAR(3), nullable=False)
    date_birth: Column[date] = Column(Date, nullable=False)
    email: Column[str] = Column(CHAR(50))
    create_date: Column[datetime] = Column(
        DateTime(timezone=True), default=func.now(), index=True
    )
    update_date: Column[datetime] = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), index=True
    )
