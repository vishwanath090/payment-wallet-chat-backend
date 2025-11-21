# app/db/base.py
from app.db.base_class import Base

# Import all models so Alembic & SQLAlchemy can see them
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
#from app.models.chat import ChatMessage  # Add this line