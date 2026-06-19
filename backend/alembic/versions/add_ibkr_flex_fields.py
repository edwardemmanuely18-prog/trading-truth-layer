from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "add_ibkr_flex_fields"
down_revision: Union[str, Sequence[str], None] = "6be0e6409ec4"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "broker_credentials",
        sa.Column(
            "flex_query_id",
            sa.String(),
            nullable=True,
        ),
    )

    op.add_column(
        "broker_credentials",
        sa.Column(
            "flex_token_encrypted",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade():

    op.drop_column(
        "broker_credentials",
        "flex_token_encrypted",
    )

    op.drop_column(
        "broker_credentials",
        "flex_query_id",
    )