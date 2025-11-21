from sqlalchemy import Column, String, Enum as SqlEnum, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from enum import Enum
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class TransactionType(str, Enum):
    ADD_MONEY = "ADD_MONEY"
    TRANSFER = "TRANSFER"
    RECEIVE = "RECEIVE"


class TransactionStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id = Column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(SqlEnum(TransactionType, name="transactiontype"), nullable=False)
    provider_tx_id = Column(String, nullable=True)

    status = Column(SqlEnum(TransactionStatus, name="transactionstatus"))
    counterparty = Column(String, nullable=True)

    # 👇 Add timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relation
    wallet = relationship("Wallet", back_populates="transactions")
