# app/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Ensure asyncpg driver is used
DATABASE_URL = settings.DATABASE_URL

# Convert to async format if missing (important!)
# Example: postgresql:// → postgresql+asyncpg://
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine for Neon
engine = create_async_engine(
    DATABASE_URL,
    echo=False,        # Disable noisy SQL logs in production
    future=True,
)

# Async session maker
async_session_maker = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)
