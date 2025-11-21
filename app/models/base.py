# app/db/base.py

from app.db.base_class import Base

# Import all models so SQLAlchemy detects them
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
