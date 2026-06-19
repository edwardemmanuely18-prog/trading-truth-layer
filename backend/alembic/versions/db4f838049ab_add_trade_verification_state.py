"""add trade verification state

Revision ID: db4f838049ab
Revises: add_ibkr_flex_fields
Create Date: 2026-06-19 01:24:07.861253

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db4f838049ab'
down_revision: Union[str, Sequence[str], None] = 'add_ibkr_flex_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.add_column(
        "trades",
        sa.Column(
            "verification_state",
            sa.String(),
            nullable=False,
            server_default="verified",
        ),
    )

    op.add_column(
        "trades",
        sa.Column(
            "evidence_trust_tier",
            sa.String(),
            nullable=False,
            server_default="tier_2",
        ),
    )

    op.add_column(
        "trades",
        sa.Column(
            "ingestion_timestamp",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade():

    op.drop_column(
        "trades",
        "ingestion_timestamp",
    )

    op.drop_column(
        "trades",
        "evidence_trust_tier",
    )

    op.drop_column(
        "trades",
        "verification_state",
    )
