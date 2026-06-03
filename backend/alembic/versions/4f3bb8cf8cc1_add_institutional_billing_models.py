"""add institutional billing models

Revision ID: 4f3bb8cf8cc1
Revises: 4825d52fd6de
Create Date: 2026-05-24 18:56:36.021463
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '4f3bb8cf8cc1'
down_revision: Union[str, Sequence[str], None] = '4825d52fd6de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.drop_column('workspaces', 'lemon_product_id')
    op.drop_column('workspaces', 'lemon_order_id')
    op.drop_column('workspaces', 'subscription_source')
    op.drop_column('workspaces', 'lemon_variant_id')


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        'workspaces',
        sa.Column('lemon_variant_id', sa.VARCHAR(), nullable=True)
    )

    op.add_column(
        'workspaces',
        sa.Column('subscription_source', sa.VARCHAR(), nullable=True)
    )

    op.add_column(
        'workspaces',
        sa.Column('lemon_order_id', sa.VARCHAR(), nullable=True)
    )

    op.add_column(
        'workspaces',
        sa.Column('lemon_product_id', sa.VARCHAR(), nullable=True)
    )