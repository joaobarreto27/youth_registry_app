from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class YouthMembersBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=15)
    t_shirt: str = Field(..., min_length=1, max_length=2)
    food_allergy: str = Field(..., min_length=1, max_length=3)
    sower: str = Field(..., min_length=1, max_length=3)
    ministry_position: str = Field(..., min_length=1, max_length=3)
    date_birth: date
    email: Optional[EmailStr] = Field(default=None, max_length=50)

    @field_validator("t_shirt")
    @classmethod
    def validate_t_shirt(cls, value):
        allowed_sizes = {"PP", "P", "M", "G", "GG", "XG", "EG", "G1", "G2", "G3", "G4"}
        if value not in allowed_sizes:
            raise ValueError("Invalid t-shirt size")
        return value

    @field_validator("food_allergy", "sower", "ministry_position")
    @classmethod
    def validate_yes_no_fields(cls, value):
        allowed: set[str] = {"Sim", "Não"}
        if value not in allowed:
            raise ValueError("Value must be 'Sim' or 'Não'")
        return value


class YouthMemberCreate(YouthMembersBase):
    pass


class YouthMemberResponse(YouthMembersBase):
    id_member: int

    class Config:
        from_attributes = True
