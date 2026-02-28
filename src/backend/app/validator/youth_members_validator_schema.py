from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class YouthMembersBase(BaseModel):
    member_name: str = Field(..., min_length=3, max_length=255)
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
        value = value.strip().upper()
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


class YouthMemberUpdate(BaseModel):
    member_name: Optional[str] = Field(default=None, min_length=3, max_length=255)
    phone_number: Optional[str] = Field(default=None, min_length=10, max_length=15)
    t_shirt: Optional[str] = Field(default=None, min_length=1, max_length=2)
    food_allergy: Optional[str] = Field(default=None, min_length=1, max_length=3)
    sower: Optional[str] = Field(default=None, min_length=1, max_length=3)
    ministry_position: Optional[str] = Field(default=None, min_length=1, max_length=3)
    date_birth: Optional[date] = None
    email: Optional[EmailStr] = Field(default=None, max_length=50)

    @field_validator("t_shirt")
    @classmethod
    def validate_t_shirt(cls, value):
        if value is None:
            return value

        allowed_sizes = {"PP", "P", "M", "G", "GG", "XG", "EG", "G1", "G2", "G3", "G4"}
        if value not in allowed_sizes:
            raise ValueError("Invalid t-shirt size")
        return value

    @field_validator("food_allergy", "sower", "ministry_position")
    @classmethod
    def validate_yes_no_fields(cls, value):
        if value is None:
            return value

        allowed = {"Sim", "Não"}
        if value not in allowed:
            raise ValueError("Value must be 'Sim' or 'Não'")
        return value

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if not any(getattr(self, field) is not None for field in self.model_fields):
            raise ValueError("At least one field must be provided for update")
        return self
