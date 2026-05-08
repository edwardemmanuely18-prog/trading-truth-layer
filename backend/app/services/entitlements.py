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

ALLOWED_PLAN_CODES = {
    "sandbox",
    "internal",
    "starter",
    "pro",
    "growth",
    "business",
}

PLAN_DEFAULTS: dict[str, dict[str, int]] = {

    "sandbox": {
        "is_public": True,
        "claims": 5,
        "trades": 1000,
        "members": 3,
        "storage_mb": 100,
    },

    "internal": {
        "is_public": False,
        "claims": 999999999,
        "trades": 999999999,
        "members": 999999999,
        "storage_mb": 999999999,
    },

    "starter": {
        "is_public": True,
        "claims": 5,
        "trades": 5000,
        "members": 3,
        "storage_mb": 500,
    },

    "pro": {
        "is_public": True,
        "claims": 50,
        "trades": 50000,
        "members": 25,
        "storage_mb": 2048,
    },

    "growth": {
        "is_public": True,
        "claims": 200,
        "trades": 250000,
        "members": 100,
        "storage_mb": 10240,
    },

    "business": {
        "is_public": True,
        "claims": 500,
        "trades": 1000000,
        "members": 250,
        "storage_mb": 51200,
    },
}


def get_public_plan_codes() -> list[str]:
    return [
        code
        for code, config in PLAN_DEFAULTS.items()
        if config.get("is_public") is True
    ]


def normalize_plan_code(plan_code: str | None) -> str:
    normalized = str(plan_code or "").strip().lower()
    return normalized if normalized in ALLOWED_PLAN_CODES else "starter"


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


def _candidate_plan_fields(workspace: Workspace) -> list[str]:
    return [
        "effective_plan_code",
        "effective_active_plan_code",
        "effective_plan",
        "active_plan_code",
        "current_plan_code",
        "configured_plan_code",
        "configured_plan",
        "plan_code",
        "plan",
    ]


def resolve_workspace_plan_code(workspace: Workspace) -> str:

    if getattr(workspace, "is_internal_workspace", 0):
        return "internal"

    for field_name in _candidate_plan_fields(workspace):
        value = getattr(workspace, field_name, None)
        normalized = normalize_plan_code(value)
        if normalized != "starter" or str(value or "").strip().lower() == "starter":
            if str(value or "").strip():
                return normalized

    return "starter"


def _positive_int_or_none(value: Any) -> int | None:
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        return None
    return int_value if int_value > 0 else None


def get_workspace_plan_limits(workspace: Workspace) -> dict[str, int]:
    plan_code = resolve_workspace_plan_code(workspace)
    plan_defaults = PLAN_DEFAULTS[plan_code]

    return {
        "claims": plan_defaults["claims"],
        "trades": plan_defaults["trades"],
        "members": plan_defaults["members"],
        "storage_mb": plan_defaults["storage_mb"],
    }


def get_workspace_raw_limit_columns(workspace: Workspace) -> dict[str, int | None]:
    return {
        "claim_limit": _positive_int_or_none(getattr(workspace, "claim_limit", None)),
        "trade_limit": _positive_int_or_none(getattr(workspace, "trade_limit", None)),
        "member_limit": _positive_int_or_none(getattr(workspace, "member_limit", None)),
        "storage_limit_mb": _positive_int_or_none(
            getattr(workspace, "storage_limit_mb", None)
        ),
    }


def get_active_trade_count(workspace_id: int, db: Session) -> int:
    return (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id)
        .count()
    )


def get_consumed_trade_count(workspace: Workspace) -> int:
    value = getattr(workspace, "trades_consumed_count", 0)
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


def get_workspace_usage_counts(workspace_id: int, db: Session) -> dict[str, int]:
    workspace = get_workspace_or_404(workspace_id, db)

    member_count = (
        db.query(WorkspaceMembership)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .count()
    )

    active_trade_count = (
        db.query(Trade)
        .filter(Trade.workspace_id == workspace_id)
        .count()
    )

    consumed_trade_count = get_consumed_trade_count(workspace)

    claim_count = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id,
            ClaimSchema.status.in_(["published", "locked"]),
        )
        .count()
    )

    storage_mb_used = 0

    return {
        "members": member_count,

        # LIVE LEDGER
        "active_trades": active_trade_count,

        # GOVERNANCE / BILLING
        "trades": consumed_trade_count,

        "claims": claim_count,
        "storage_mb": storage_mb_used,
    }


def build_entitlement_snapshot(workspace_id: int, db: Session) -> dict[str, Any]:
    workspace = get_workspace_or_404(workspace_id, db)
    resolved_plan_code = resolve_workspace_plan_code(workspace)
    limits = get_workspace_plan_limits(workspace)
    usage = get_workspace_usage_counts(workspace_id, db)
    billing_status = normalize_billing_status(workspace.billing_status)

    return {
        "workspace_id": workspace.id,
        "plan_code": resolved_plan_code,
        "billing_status": billing_status,
        "access": {
            "has_active_access": workspace_has_active_access(workspace),
            "has_soft_warning_access": workspace_has_soft_warning_access(workspace),
            "is_restricted": workspace_is_restricted(workspace),
        },
        "limits": limits,
        "usage": usage,
        "diagnostics": {
            "resolved_plan_code": resolved_plan_code,
            "raw_limit_columns": get_workspace_raw_limit_columns(workspace),
            "defaults_for_resolved_plan": PLAN_DEFAULTS[resolved_plan_code],
        },
    }


def enforce_workspace_billing_access(
    workspace_id: int,
    db: Session,
    *,
    allow_past_due: bool = True,
    action_label: str = "perform this action",
) -> Workspace:
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
            detail={
                "code": "claim_limit_reached",
                "resource": resource_label,
                "message": f"Claim limit reached for your current plan",
                "workspace_id": workspace_id,
                "used": used,
                "limit": limit,
                "upgrade_required": True,
                "type": "PLAN_LIMIT",
            },
        )


def enforce_claim_creation_allowed(
    workspace_id: int,
    db: Session,
) -> Workspace:
    """
    Draft claim creation:
    - Allowed in sandbox (no billing)
    - Enforces ONLY capacity limits
    """

    workspace = get_workspace_or_404(workspace_id, db)

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
    incoming_count: int,
) -> Workspace:

    workspace = enforce_workspace_billing_access(
        workspace_id,
        db,
        allow_past_due=True,
        action_label="import additional trades",
    )

    usage = get_workspace_usage_counts(
        workspace_id,
        db,
    )

    limits = get_workspace_plan_limits(
        workspace
    )

    enforce_limit_not_reached(
        used=usage["trades"],
        limit=limits["trades"],
        resource_label="trade",
        workspace_id=workspace_id,
        requested_additional=max(
            int(incoming_count),
            1,
        ),
    )

    return workspace
    

def enforce_readonly_access_allowed(
    workspace_id: int,
    db: Session,
) -> Workspace:
    return get_workspace_or_404(workspace_id, db)

def enforce_storage_limit(
    workspace_id: int,
    db: Session,
    *,
    additional_mb: int = 1,
) -> Workspace:
    workspace = enforce_workspace_billing_access(
        workspace_id,
        db,
        allow_past_due=True,
        action_label="upload more evidence",
    )

    usage = get_workspace_usage_counts(workspace_id, db)
    limits = get_workspace_plan_limits(workspace)

    enforce_limit_not_reached(
        used=usage["storage_mb"],
        limit=limits["storage_mb"],
        resource_label="storage",
        workspace_id=workspace_id,
        requested_additional=max(int(additional_mb), 1),
    )

    return workspace    