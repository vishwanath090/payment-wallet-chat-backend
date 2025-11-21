"""Add created_at to transactions

Revision ID: 786ca2aa74d0
Revises: 1f2d920780e5
Create Date: 2025-11-17 14:11:44.902979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '786ca2aa74d0'
down_revision: Union[str, Sequence[str], None] = '1f2d920780e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
