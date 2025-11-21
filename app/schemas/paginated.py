from pydantic import BaseModel
from typing import List, Optional
from app.schemas.transaction import TransactionRead

class PaginatedTransactions(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    next_page: Optional[int]
    prev_page: Optional[int]
    data: List[TransactionRead]

    model_config = {"from_attributes": True}

