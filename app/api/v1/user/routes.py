# app/api/v1/user/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.core.jwt import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def list_users(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.id != current_user.id)
    )
    users = result.scalars().all()
    return [{"email": user.email, "full_name": user.full_name} for user in users]
