from pydantic import BaseModel, EmailStr
from uuid import UUID
from decimal import Decimal
from typing import Optional

class AddMoneyRequest(BaseModel):
    amount: float
    pin: str  # Make sure this is here

class TransferRequest(BaseModel):
    to_email: EmailStr
    amount: float
    pin: str  # Make sure this is here

class WalletRead(BaseModel):
    id: UUID
    user_id: UUID
    balance: float

    model_config = {"from_attributes": True}

class TransactionRead(BaseModel):
    id: UUID
    wallet_id: UUID
    amount: float
    type: str
    status: str
    provider_tx_id: Optional[str] = None
    counterparty: Optional[str] = None

    model_config = {"from_attributes": True}

class PaginatedTransactions(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    next_page: Optional[int] = None
    prev_page: Optional[int] = None
    data: list[TransactionRead]