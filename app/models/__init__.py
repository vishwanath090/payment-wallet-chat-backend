from app.models.base import Base

# FORCE IMPORT all model modules (ensures metadata is populated)
import app.models.user
import app.models.wallet
import app.models.transaction


# Expose metadata for Alembic
metadata = Base.metadata
