from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership


ACTIVE_BILLING_STATUSES = {"active", "trialing"}
SOFT_WARNING_BILLING_STATUSES = {"past_due"}
RESTRICTED_BILLING_STATUSES = {"inactive", "canceled", "unpaid", "pending_manual_review"}


def normalize_plan_code(plan_code: str | None) -> str:
    normalized = str(plan_code or "").strip().lower()
    allowed = {"starter", "pro", "growth", "business"}
    return normalized if normalized in allowed else "starter"


def normalize_billing_status(status: str | None) -> str:
    normalized = str(status or "").strip().lower()
    allowed = (
        ACTIVE_BILLING_STATUSES
        | SOFT_WARNING_BILLING_STATUSES
        | RESTRICTED_BILLING_STATUSES
    )
    return normalized if normalized in allowed else "inactive"


def get_workspace_or_404(workspace_id: int, db: Session) -> Workspace:
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


def get_workspace_membership(
    workspace_id: int,
    user_id: int,
    db: Session,
) -> WorkspaceMembership | None:
    return (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )


def workspace_has_active_access(workspace: Workspace) -> bool:
    return normalize_billing_status(workspace.billing_status) in ACTIVE_BILLING_STATUSES


def workspace_has_soft_warning_access(workspace: Workspace) -> bool:
    return normalize_billing_status(workspace.billing_status) in SOFT_WARNING_BILLING_STATUSES


def workspace_is_restricted(workspace: Workspace) -> bool:
    return normalize_billing_status(workspace.billing_status) in RESTRICTED_BILLING_STATUSES


def get_workspace_plan_limits(workspace: Workspace) -> dict[str, int]:
    """
    Source of truth for operational limits.

    We prefer explicit workspace fields if they exist and are > 0, because your
    current app already persists those values on the workspace row. If any are
    missing or zero, we fall back to plan defaults.
    """
    plan_code = normalize_plan_code(getattr(workspace, "plan_code", None))

    defaults = {
        "starter": {
            "claims": 5,
            "trades": 1000,
            "members": 3,
            "storage_mb": 500,
        },
        "pro": {
            "claims": 25,
            "trades": 10000,
            "members": 10,
            "storage_mb": 5000,
        },
        "growth": {
            "claims": 100,
            "trades": 100000,
            "members": 50,
            "storage_mb": 25000,
        },
        "business": {
            "claims": 500,
            "trades": 1000000,
            "members": 250,
            "storage_mb": 100000,
        },
    }

    plan_defaults = defaults[plan_code]

    claim_limit = int(getattr(workspace, "claim_limit", 0) or 0)
    trade_limit = int(getattr(workspace, "trade_limit", 0) or 0)
    member_limit = int(getattr(workspace, "member_limit", 0) or 0)
    storage_limit_mb = int(getattr(workspace, "storage_limit_mb", 0) or 0)

    return {
        "claims": claim_limit if claim_limit > 0 else plan_defaults["claims"],
        "trades": trade_limit if trade_limit > 0 else plan_defaults["trades"],
        "members": member_limit if member_limit > 0 else plan_defaults["members"],
        "storage_mb": (
            storage_limit_mb if storage_limit_mb > 0 else plan_defaults["storage_mb"]
        ),
    }


def get_workspace_usage_counts(workspace_id: int, db: Session) -> dict[str, int]:
    member_count = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .count()
    )

    trade_count = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id)
        .count()
    )

    claim_count = (
        db.query(ClaimSchema)
        .filter(ClaimSchema.workspace_id == workspace_id)
        .count()
    )

    # Storage calculation is not wired in your current schema yet.
    storage_mb_used = 0

    return {
        "members": member_count,
        "trades": trade_count,
        "claims": claim_count,
        "storage_mb": storage_mb_used,
    }


def build_entitlement_snapshot(workspace_id: int, db: Session) -> dict[str, Any]:
    workspace = get_workspace_or_404(workspace_id, db)
    limits = get_workspace_plan_limits(workspace)
    usage = get_workspace_usage_counts(workspace_id, db)
    billing_status = normalize_billing_status(workspace.billing_status)

    return {
        "workspace_id": workspace.id,
        "plan_code": normalize_plan_code(workspace.plan_code),
        "billing_status": billing_status,
        "access": {
            "has_active_access": workspace_has_active_access(workspace),
            "has_soft_warning_access": workspace_has_soft_warning_access(workspace),
            "is_restricted": workspace_is_restricted(workspace),
        },
        "limits": limits,
        "usage": usage,
    }


def enforce_workspace_billing_access(
    workspace_id: int,
    db: Session,
    *,
    allow_past_due: bool = True,
    action_label: str = "perform this action",
) -> Workspace:
    """
    Hard gate for paid operations.

    active / trialing => allowed
    past_due => allowed only if allow_past_due=True
    inactive / canceled / unpaid / pending_manual_review => blocked
    """
    workspace = get_workspace_or_404(workspace_id, db)
    billing_status = normalize_billing_status(workspace.billing_status)

    if billing_status in ACTIVE_BILLING_STATUSES:
        return workspace

    if billing_status in SOFT_WARNING_BILLING_STATUSES and allow_past_due:
        return workspace

    if billing_status == "pending_manual_review":
        raise HTTPException(
            status_code=403,
            detail=(
                f"Workspace billing is pending manual review. "
                f"You cannot {action_label} yet."
            ),
        )

    raise HTTPException(
        status_code=403,
        detail=(
            f"Workspace billing status is '{billing_status}'. "
            f"You cannot {action_label} until billing is active."
        ),
    )


def enforce_limit_not_reached(
    *,
    used: int,
    limit: int,
    resource_label: str,
    workspace_id: int,
    requested_additional: int = 1,
) -> None:
    if limit <= 0:
        return

    projected = used + requested_additional
    if projected > limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"{resource_label.capitalize()} limit reached for workspace {workspace_id}. "
                f"Current usage: {used}. "
                f"Requested additional: {requested_additional}. "
                f"Plan limit: {limit}. "
                f"Upgrade workspace plan to continue."
            ),
        )


def enforce_claim_creation_allowed(
    workspace_id: int,
    db: Session,
) -> Workspace:
    workspace = enforce_workspace_billing_access(
        workspace_id,
        db,
        allow_past_due=True,
        action_label="create additional claims",
    )

    usage = get_workspace_usage_counts(workspace_id, db)
    limits = get_workspace_plan_limits(workspace)

    enforce_limit_not_reached(
        used=usage["claims"],
        limit=limits["claims"],
        resource_label="claim",
        workspace_id=workspace_id,
        requested_additional=1,
    )

    return workspace


def enforce_member_invite_allowed(
    workspace_id: int,
    db: Session,
) -> Workspace:
    workspace = enforce_workspace_billing_access(
        workspace_id,
        db,
        allow_past_due=True,
        action_label="invite additional members",
    )

    usage = get_workspace_usage_counts(workspace_id, db)
    limits = get_workspace_plan_limits(workspace)

    enforce_limit_not_reached(
        used=usage["members"],
        limit=limits["members"],
        resource_label="member",
        workspace_id=workspace_id,
        requested_additional=1,
    )

    return workspace


def enforce_trade_import_allowed(
    workspace_id: int,
    db: Session,
    *,
    additional_trades: int = 1,
) -> Workspace:
    workspace = enforce_workspace_billing_access(
        workspace_id,
        db,
        allow_past_due=True,
        action_label="import or create more trades",
    )

    usage = get_workspace_usage_counts(workspace_id, db)
    limits = get_workspace_plan_limits(workspace)

    enforce_limit_not_reached(
        used=usage["trades"],
        limit=limits["trades"],
        resource_label="trade",
        workspace_id=workspace_id,
        requested_additional=max(int(additional_trades), 1),
    )

    return workspace


def enforce_readonly_access_allowed(
    workspace_id: int,
    db: Session,
) -> Workspace:
    """
    Read-only access remains allowed even when billing is inactive/canceled.
    This keeps dashboards, evidence, and history visible.
    """
    return get_workspace_or_404(workspace_id, db)