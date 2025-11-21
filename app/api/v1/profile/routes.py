# app/api/v1/profile/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.jwt import get_current_user
from app.models.user import User
from app.schemas.profile import (
    ProfileResponse, 
    ProfileUpdate, 
    VerifyPINRequest,
    VerifyPasswordRequest,
    ChangePasswordRequest,
    ResetPasswordByPinRequest
)
from sqlalchemy import select  # ⬅️ ADD THIS


from app.core.security import verify_password, hash_password, verify_pin

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("/", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile information
    """
    try:
        return ProfileResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            mobile_number=current_user.mobile_number,
            is_active=current_user.is_active
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}"
        )

@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user full name / mobile number
    """
    try:
        # Update full name
        if profile_data.full_name is not None:
            # full name cannot be empty or only spaces
            if profile_data.full_name.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Full name cannot be empty"
                )

            # optional: limit name length
            if len(profile_data.full_name) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Full name cannot exceed 50 characters"
                )

            current_user.full_name = profile_data.full_name.strip()

        # Update mobile number
        if profile_data.mobile_number is not None:
            if (
                len(profile_data.mobile_number) != 10 or 
                not profile_data.mobile_number.isdigit()
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Mobile number must be exactly 10 digits"
                )
            
            current_user.mobile_number = profile_data.mobile_number
        
        await db.commit()
        await db.refresh(current_user)

        return ProfileResponse(
            id=current_user.id,
            email=current_user.email,
            full_name=current_user.full_name,
            mobile_number=current_user.mobile_number,
            is_active=current_user.is_active
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.post("/verify-pin")
async def verify_user_pin(
    pin_data: VerifyPINRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user's transaction PIN
    """
    try:
        # FIX: Use pin_hashed instead of pin_hash
        if not current_user.pin_hashed:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PIN not set for this user"
            )
        
        # Validate PIN format
        if len(pin_data.pin) != 4 or not pin_data.pin.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN must be exactly 4 digits"
            )
        
        # FIX: Use pin_hashed instead of pin_hash
        if not verify_pin(pin_data.pin, current_user.pin_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid PIN"
            )
        
        return {"message": "PIN verified successfully", "verified": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PIN verification failed: {str(e)}"
        )

@router.post("/verify-password")
async def verify_user_password(
    password_data: VerifyPasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify user's password
    """
    try:
        if not password_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )
        
        if not verify_password(password_data.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        return {"message": "Password verified successfully", "verified": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Password verification failed: {str(e)}"
        )

@router.put("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if len(password_data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )
        
        # Update to new password
        current_user.hashed_password = hash_password(password_data.new_password)
        await db.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )

@router.post("/reset-password-with-pin")
async def reset_password_with_pin(
    data: ResetPasswordByPinRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password from login page using:
    - email
    - full name
    - 4-digit PIN

    This endpoint does NOT require JWT token
    (can be called before login).
    """
    try:
        # 1) Find user by email
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            # To avoid account enumeration, use generic message
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or details incorrect"
            )

        # 2) Check full name (trimmed, case-insensitive)
        if not user.full_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Full name not set for this user"
            )

        if user.full_name.strip().lower() != data.full_name.strip().lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or details incorrect"
            )

        # 3) Check PIN presence
        if not getattr(user, "pin_hashed", None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN is not set for this user"
            )

        # 4) Validate PIN format
        if len(data.pin) != 4 or not data.pin.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PIN must be exactly 4 digits"
            )

        # 5) Verify PIN
        if not verify_pin(data.pin, user.pin_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or details incorrect"
            )

        # 6) Validate new password (extra validation if you want)
        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters long"
            )

        # 7) Update password
        user.hashed_password = hash_password(data.new_password)
        await db.commit()
        await db.refresh(user)

        return {"message": "Password reset successfully"}

    except HTTPException:
        # re-raise known HTTP errors
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
