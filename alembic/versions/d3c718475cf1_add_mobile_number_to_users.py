"""add_mobile_number_to_users

Revision ID: d3c718475cf1
Revises: 786ca2aa74d0
Create Date: 2025-11-17 22:20:31.694788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3c718475cf1'
down_revision: Union[str, Sequence[str], None] = '786ca2aa74d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
