from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    pin: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    mobile_number: Optional[str] = None

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PinVerifyRequest(BaseModel):
    pin: str

class UpdateProfileRequest(BaseModel):
    mobile_number: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserProfileResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    mobile_number: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}

