"""add broker accounts

Revision ID: 6be0e6409ec4
Revises: ca03c2c77597
Create Date: 2026-06-16 13:46:28.927872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6be0e6409ec4'
down_revision: Union[str, Sequence[str], None] = 'ca03c2c77597'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
