"""add import jobs

Revision ID: f1de2adb441e
Revises: 4f3bb8cf8cc1
Create Date: 2026-06-14 19:08:29.952495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1de2adb441e'
down_revision: Union[str, Sequence[str], None] = '4f3bb8cf8cc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "import_jobs",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "adapter_provider",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "filename",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "file_type",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="uploaded",
        ),

        sa.Column(
            "records_detected",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "imported_records",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
    )


def downgrade() -> None:

    op.drop_table(
        "import_jobs"
    )
