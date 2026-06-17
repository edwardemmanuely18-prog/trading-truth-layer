"""add ibkr credential fields

Revision ID: ca03c2c77597
Revises: 28754d91264b
Create Date: 2026-06-16 13:07:51.716181

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca03c2c77597'
down_revision: Union[str, Sequence[str], None] = '28754d91264b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
