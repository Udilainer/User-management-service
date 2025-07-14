from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing import List, Any, Annotated


def check_not_bool(v: Any) -> Any:
    if isinstance(v, bool):
        raise ValueError("ID cannot be a boolean value. Please provide an integer.")
    return v


class HealthStatus(BaseModel):
    status: str


class UserBase(BaseModel):
    name: str = Field(
        min_length=3,
        json_schema_extra={"example": "John Doe"},
        validation_alias='name',
        description="The full name of the user, must be at least 3 characters long."
    )
    email: EmailStr = Field(
        json_schema_extra={"example": "user@example.com"},
        description="The user's email address."
    )


class UserCreate(UserBase):
    id: Annotated[int, BeforeValidator(check_not_bool)] = Field(
        gt=0,
        json_schema_extra={"example": 101},
        description="A unique positive integer identifying the user."
    )


class UserResponse(UserBase):
    id: int

    class ConfigDict:
        from_attributes = True


class UserSetupPayload(BaseModel):
    users: List[UserCreate]
