from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from typing import Optional, List

# Use enums ONLY from models
from app.models.transaction import TransactionType, TransactionStatus


class TransactionRead(BaseModel):
    id: UUID
    wallet_id: UUID
    amount: Decimal
    type: TransactionType
    status: TransactionStatus

    provider_tx_id: Optional[str] = None
    counterparty: Optional[str] = None

    model_config = {"from_attributes": True}


class TransactionHistoryResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    next_page: Optional[int]
    prev_page: Optional[int]
    data: List[TransactionRead]
