from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal
from enum import Enum
from app.models.transaction import Transaction, TransactionType,TransactionStatus
from typing import List
class TransactionType(str, Enum):
    ADD_MONEY = "ADD_MONEY"
    TRANSFER = "TRANSFER"
    RECEIVE = "RECEIVE"


class TransactionRead(BaseModel):
    id: UUID
    wallet_id: UUID
    amount: Decimal
    type: TransactionType
    status: TransactionStatus = TransactionStatus

    provider_tx_id: str | None = None
    counterparty: str | None = None

    model_config = {"from_attributes": True}
class TransactionHistoryResponse(BaseModel):
    page: int
    limit: int
    total_items: int
    total_pages: int
    next_page: int | None
    prev_page: int | None
    items: List[TransactionRead]