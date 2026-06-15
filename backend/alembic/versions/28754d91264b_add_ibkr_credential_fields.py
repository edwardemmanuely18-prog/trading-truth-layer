"""add ibkr credential fields

Revision ID: 28754d91264b
Revises: f1de2adb441e
Create Date: 2026-06-15 22:02:07.366800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28754d91264b'
down_revision: Union[str, Sequence[str], None] = 'f1de2adb441e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
