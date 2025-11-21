# app/schemas/profile.py
from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

class ProfileResponse(BaseModel):
    id: uuid.UUID  # Changed to UUID to match your model
    email: EmailStr
    full_name: Optional[str] = None  # Made optional since your model allows null
    mobile_number: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    mobile_number: Optional[str] = None

class VerifyPINRequest(BaseModel):
    pin: str

class VerifyPasswordRequest(BaseModel):
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class ResetPasswordByPinRequest(BaseModel):
    email: EmailStr
    full_name: str
    pin: str
    new_password: str
