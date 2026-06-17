from alembic import op
import sqlalchemy as sa


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