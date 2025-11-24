from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    pin: str = Field(..., min_length=4, max_length=4, regex=r'^\d{4}$')

class UserRead(BaseModel):
    id: UUID
    full_name: Optional[str]
    email: EmailStr
    is_active: bool

    model_config = {"from_attributes": True}
