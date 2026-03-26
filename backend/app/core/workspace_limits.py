from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.models.trade import Trade
from app.models.claim_schema import ClaimSchema


def is_workspace_active(workspace: Workspace) -> bool:
    return workspace.billing_status in {"active", "trialing"}


def check_claim_limit(db: Session, workspace: Workspace) -> tuple[bool, str | None]:
    count = db.query(ClaimSchema).filter(
        ClaimSchema.workspace_id == workspace.id
    ).count()

    if count >= workspace.claim_limit:
        return False, "Claim limit reached. Upgrade your plan."

    return True, None


def check_trade_limit(db: Session, workspace: Workspace) -> tuple[bool, str | None]:
    count = db.query(Trade).filter(
        Trade.workspace_id == workspace.id
    ).count()

    if count >= workspace.trade_limit:
        return False, "Trade limit reached. Upgrade your plan."

    return True, None


def check_member_limit(db: Session, workspace: Workspace) -> tuple[bool, str | None]:
    count = db.query(WorkspaceMembership).filter(
        WorkspaceMembership.workspace_id == workspace.id
    ).count()

    if count >= workspace.member_limit:
        return False, "Member limit reached. Upgrade your plan."

    return True, None


def enforce_workspace_active(workspace: Workspace) -> tuple[bool, str | None]:
    if not is_workspace_active(workspace):
        return False, "Workspace billing inactive. Upgrade required."
    return True, None