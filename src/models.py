from pydantic import BaseModel, EmailStr

class HealthStatus(BaseModel):
    status: str

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    id: int

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True