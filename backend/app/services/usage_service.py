from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.workspace import Workspace
from app.models.workspace_membership import (
    WorkspaceMembership,
)


def get_workspace_usage(
    db: Session,
    workspace_id: int,
):
    """
    Canonical workspace usage snapshot.

    Usage metrics are workspace-governance
    metrics and therefore count every object
    that consumes workspace resources.

    Claims:
        - counts ALL claim lifecycle states

    Trades:
        - immutable consumed trade count

    Ledger Trades:
        - live mutable trade ledger count

    Members:
        - active workspace memberships
    """

    #
    # CLAIMS
    #

    claim_count = (
        db.query(
            func.count(
                ClaimSchema.id,
            )
        )
        .filter(
            ClaimSchema.workspace_id
            == workspace_id
        )
        .scalar()
    ) or 0

    #
    # WORKSPACE
    #

    workspace = (
        db.query(
            Workspace,
        )
        .filter(
            Workspace.id
            == workspace_id
        )
        .first()
    )

    #
    # GOVERNED TRADE COUNT
    #

    consumed_trade_count = int(
        getattr(
            workspace,
            "trades_consumed_count",
            0,
        ) or 0
    )

    #
    # LIVE LEDGER COUNT
    #

    ledger_trade_count = (
        db.query(
            func.count(
                Trade.id,
            )
        )
        .filter(
            Trade.workspace_id
            == workspace_id
        )
        .scalar()
    ) or 0

    #
    # MEMBERS
    #

    member_count = (
        db.query(
            func.count(
                WorkspaceMembership.id,
            )
        )
        .filter(
            WorkspaceMembership.workspace_id
            == workspace_id
        )
        .scalar()
    ) or 0

    #
    # RESPONSE
    #

    return {

        "claims":
            claim_count,

        "trades":
            consumed_trade_count,

        "ledger_trades":
            ledger_trade_count,

        "members":
            member_count,

    }