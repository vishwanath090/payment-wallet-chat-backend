from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.core.security import hash_pin
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    pin_hashed = Column(String, nullable=False)
    # FIX — must match Wallet.back_populates
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    mobile_number = Column(String(15), nullable=True)