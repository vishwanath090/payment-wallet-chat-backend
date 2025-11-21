# app/services/user_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash, verify_password

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    user = res.scalars().first()
    return user

async def create_user(db: AsyncSession, email: str, password: str, full_name: str | None = None) -> User:
    hashed = get_password_hash(password)
    user = User(email=email, hashed_password=hashed, full_name=full_name or None)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
