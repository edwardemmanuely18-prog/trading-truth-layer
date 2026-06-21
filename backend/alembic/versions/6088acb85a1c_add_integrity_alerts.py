from alembic import op
import sqlalchemy as sa


revision = "6088acb85a1c"

down_revision = "db4f838049ab"

branch_labels = None

depends_on = None


def upgrade():

    op.create_table(
        "integrity_alerts",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
        ),

        sa.Column(
            "workspace_id",
            sa.Integer(),
            nullable=False,
            index=True,
        ),

        sa.Column(
            "severity",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "alert_type",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "entity_type",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "entity_id",
            sa.String(),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False,
            server_default="open",
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
        ),

        sa.Column(
            "resolved_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade():

    op.drop_table(
        "integrity_alerts"
    )