from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, hash_pin, verify_pin
from app.core.jwt import get_current_user, create_access_token
from app.schemas.auth import (
    UserCreate, UserLogin, UserRead, TokenResponse, PinVerifyRequest,
    UpdateProfileRequest, ChangePasswordRequest, UserProfileResponse,
    RefreshTokenRequest
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# --------------------
# SIGNUP
# --------------------
from app.core.security import hash_password, verify_password, hash_pin  # 👈 add hash_pin
@router.post("/signup", response_model=UserRead, status_code=201)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        pin_hashed=hash_pin(user_data.pin),
    )

    db.add(new_user)
    await db.flush()

    # Create wallet
    from app.models.wallet import Wallet
    wallet = Wallet(user_id=new_user.id, balance=0)
    db.add(wallet)

    await db.commit()
    await db.refresh(new_user)

    return new_user



# --------------------
# LOGIN  (THIS WAS MISSING)
# --------------------
# login/route.py

from app.core.jwt import create_access_token, create_refresh_token

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
# login/route.py

from app.core.jwt import verify_refresh_token, create_access_token
from app.schemas.auth import RefreshTokenRequest, TokenResponse

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest):
    user_id = verify_refresh_token(data.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    new_access_token = create_access_token({"sub": str(user_id)})
    return TokenResponse(access_token=new_access_token)
from pydantic import BaseModel
from fastapi import Body

class PinInput(BaseModel):
    pin: str
