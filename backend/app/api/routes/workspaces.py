from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_membership import WorkspaceMembership
from app.services.audit_service import log_audit_event
from app.services.entitlements import (
    normalize_plan_code,
    normalize_billing_status,
    resolve_workspace_plan_code,
    build_entitlement_snapshot,
    get_workspace_plan_limits,
    get_workspace_usage_counts,
)
from app.services.metrics_service import (
    get_workspace_trade_metrics,
)

from secrets import token_urlsafe

from app.models.workspace_invite import WorkspaceInvite


from fastapi import HTTPException

router = APIRouter()


class CreateWorkspacePayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class UpdateWorkspaceSettingsPayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    billing_email: str | None = Field(default=None, max_length=255)


class UpdateWorkspaceMemberRolePayload(BaseModel):
    role: str = Field(min_length=1, max_length=50)


def require_workspace_member(workspace_id: int, current_user: User, db: Session):
    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == current_user.id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=403, detail="User is not a member of this workspace")

    return membership


def require_workspace_owner(workspace_id: int, current_user: User, db: Session):
    membership = require_workspace_member(workspace_id, current_user, db)
    if membership.role != "owner":
        raise HTTPException(status_code=403, detail="Owner role required for this workspace")
    return membership


def enforce_internal_workspace_access(
    workspace: Workspace,
    current_user: User,
    db: Session,
):
    """
    Internal workspaces are restricted to owners only.
    Prevents non-owner access even if user knows the URL.
    """

    if not getattr(workspace, "is_internal_workspace", False):
        return

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace.id,
            WorkspaceMembership.user_id == current_user.id,
            WorkspaceMembership.role == "owner",
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Internal workspace restricted to owners only",
        )


def serialize_workspace_member(membership: WorkspaceMembership, user: User):
    return {
        "workspace_id": membership.workspace_id,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "global_role": user.role,
        "workspace_role": membership.role,
    }


def normalize_workspace_role(value: str | None) -> str:
    normalized = str(value or "").strip().lower()
    allowed_roles = {"owner", "operator", "member", "auditor"}
    return normalized if normalized in allowed_roles else "member"


def serialize_workspace_settings(workspace: Workspace):
    limits = get_workspace_plan_limits(workspace)

    return {
        "workspace_id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "billing_email": workspace.billing_email,

        "plan_code": resolve_workspace_plan_code(workspace),
        "billing_status": normalize_billing_status(
            workspace.billing_status
        ),

        "limits": limits,

        "stripe_customer_id": workspace.stripe_customer_id,
        "stripe_subscription_id": workspace.stripe_subscription_id,

        "subscription_current_period_end": (
            workspace.subscription_current_period_end.isoformat()
            if workspace.subscription_current_period_end
            else None
        ),

        "created_at": (
            workspace.created_at.isoformat()
            if workspace.created_at
            else None
        ),

        "updated_at": (
            workspace.updated_at.isoformat()
            if workspace.updated_at
            else None
        ),
    }
    plan = get_plan_definition(plan_code)

    limit_key_map = {
        "members": "member_limit",
        "trades": "trade_limit",
        "active_trades": "trade_limit",
        "claims": "claim_limit",
        "storage_mb": "storage_limit_mb",
    }

    limit_key = limit_key_map[dimension]
    limit = plan["limits"][limit_key]

    if not limit or limit <= 0:
        ratio = None
        status = "unlimited"
    else:
        ratio = round(used / limit, 4)
        if used > limit:
            status = "over_limit"
        elif used == limit:
            status = "at_limit"
        elif used / limit >= 0.8:
            status = "near_limit"
        else:
            status = "ok"

    return {
        "used": used,
        "limit": limit,
        "ratio": ratio,
        "status": status,
    }


def build_upgrade_recommendation(
    configured_plan_code: str,
    effective_plan_code: str,
    usage_summary: dict,
    plan_mismatch: bool = False,
):
    current_order = get_plan_order()
    configured_normalized = normalize_plan_code(configured_plan_code)
    effective_normalized = normalize_plan_code(effective_plan_code)

    configured_index = current_order.index(configured_normalized)
    effective_index = current_order.index(effective_normalized)

    configured_breached_dimensions = []
    configured_near_limit_dimensions = []

    for key, row in usage_summary.items():
        if key == "active_trades":
            continue
        configured_row = usage_row_for_plan(configured_normalized, row["used"], key)

        if configured_row["status"] == "over_limit":
            configured_breached_dimensions.append(key)
        elif configured_row["status"] in {"at_limit", "near_limit"}:
            configured_near_limit_dimensions.append(key)

    configured_has_breaches = len(configured_breached_dimensions) > 0
    configured_has_near_limits = len(configured_near_limit_dimensions) > 0

    if plan_mismatch and configured_index > effective_index:
        if not configured_has_breaches and not configured_has_near_limits:
            configured_plan = get_plan_definition(configured_normalized)
            return {
                "current_plan_code": configured_normalized,
                "effective_plan_code": effective_normalized,
                "recommendation_basis_plan_code": configured_normalized,
                "recommended_plan_code": configured_normalized,
                "recommended_plan_name": configured_plan["name"],
                "recommended_plan_is_distinct": False,
                "upgrade_required_now": False,
                "upgrade_recommended_soon": False,
                "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                "already_at_highest_tier": configured_index >= len(current_order) - 1,
                "breached_dimensions": [],
                "near_limit_dimensions": [],
            }

        if configured_has_near_limits and not configured_has_breaches:
            if configured_index < len(current_order) - 1:
                recommended_index = configured_index + 1
                recommended_plan = get_plan_definition(current_order[recommended_index])
                return {
                    "current_plan_code": configured_normalized,
                    "effective_plan_code": effective_normalized,
                    "recommendation_basis_plan_code": configured_normalized,
                    "recommended_plan_code": recommended_plan["code"],
                    "recommended_plan_name": recommended_plan["name"],
                    "recommended_plan_is_distinct": True,
                    "upgrade_required_now": False,
                    "upgrade_recommended_soon": True,
                    "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                    "already_at_highest_tier": False,
                    "breached_dimensions": [],
                    "near_limit_dimensions": configured_near_limit_dimensions,
                }

            configured_plan = get_plan_definition(configured_normalized)
            return {
                "current_plan_code": configured_normalized,
                "effective_plan_code": effective_normalized,
                "recommendation_basis_plan_code": configured_normalized,
                "recommended_plan_code": configured_plan["code"],
                "recommended_plan_name": configured_plan["name"],
                "recommended_plan_is_distinct": False,
                "upgrade_required_now": False,
                "upgrade_recommended_soon": False,
                "billing_activation_recommended": configured_normalized not in {"sandbox", "starter"},
                "already_at_highest_tier": True,
                "breached_dimensions": [],
                "near_limit_dimensions": configured_near_limit_dimensions,
            }

    current_index = max(configured_index, effective_index)
    current_normalized = current_order[current_index]

    breached_dimensions = []
    near_limit_dimensions = []

    for key, row in usage_summary.items():
        if key == "active_trades":
            continue
        used = row["used"]
        limit = row["limit"]
        ratio = row["ratio"]

        if limit and limit > 0 and used > limit:
            breached_dimensions.append(key)
        elif limit and limit > 0 and ratio is not None and ratio >= 0.8:
            near_limit_dimensions.append(key)

    has_breaches = len(breached_dimensions) > 0
    has_near_limits = len(near_limit_dimensions) > 0
    already_at_highest_tier = current_index >= len(current_order) - 1

    if (has_breaches or has_near_limits) and not already_at_highest_tier:
        recommended_index = current_index + 1
    else:
        recommended_index = current_index

    recommended_plan_code = current_order[recommended_index]
    recommended_plan = get_plan_definition(recommended_plan_code)
    has_distinct_recommendation = recommended_plan_code != current_normalized

    return {
        "current_plan_code": configured_normalized,
        "effective_plan_code": effective_normalized,
        "recommendation_basis_plan_code": current_normalized,
        "recommended_plan_code": recommended_plan_code,
        "recommended_plan_name": recommended_plan["name"],
        "recommended_plan_is_distinct": has_distinct_recommendation,
        "upgrade_required_now": has_breaches and has_distinct_recommendation,
        "upgrade_recommended_soon": (not has_breaches) and has_near_limits and has_distinct_recommendation,
        "billing_activation_recommended": (
            plan_mismatch
            and configured_index > effective_index
            and not has_distinct_recommendation
            and configured_normalized not in {"sandbox", "starter"}
        ),
        "already_at_highest_tier": already_at_highest_tier,
        "breached_dimensions": breached_dimensions,
        "near_limit_dimensions": near_limit_dimensions,

        "billing_activation_recommended": (
            configured_normalized not in {"sandbox", "starter"}
        ),
    }


@router.get("/workspaces")
def list_my_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(WorkspaceMembership, Workspace)
        .join(Workspace, Workspace.id == WorkspaceMembership.workspace_id)
        .filter(WorkspaceMembership.user_id == current_user.id)
        .order_by(Workspace.id.asc())
        .all()
    )

    visible_rows = []

    for membership, workspace in rows:

        if getattr(workspace, "is_internal_workspace", False):
            if membership.role != "owner":
                continue

        visible_rows.append({
            "workspace_id": workspace.id,
            "workspace_name": workspace.name,
            "workspace_role": membership.role,
        })

    return visible_rows


@router.post("/workspaces")
def create_workspace(
    payload: CreateWorkspacePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = Workspace(
        name=payload.name.strip(),
        plan_code="sandbox",
        billing_status="inactive",
        claim_limit=5,
        trade_limit=1000,
        member_limit=3,
        storage_limit_mb=100,
    )
    db.add(workspace)
    db.flush()

    membership = WorkspaceMembership(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(membership)

    db.commit()
    db.refresh(workspace)

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "workspace_role": "owner",
    }


@router.get("/workspaces/{workspace_id}/dashboard")
def get_workspace_dashboard(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    member_count = db.query(WorkspaceMembership).filter(
        WorkspaceMembership.workspace_id == workspace_id
    ).count()
    trade_count = db.query(Trade).filter(Trade.workspace_id == workspace_id).count()
    claim_count = db.query(ClaimSchema).filter(ClaimSchema.workspace_id == workspace_id).count()

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "member_count": member_count,
        "trade_count": trade_count,
        "claim_count": claim_count,
    }


@router.get("/workspaces/{workspace_id}/settings")
def get_workspace_settings(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    return serialize_workspace_settings(workspace)


@router.patch("/workspaces/{workspace_id}/settings")
def update_workspace_settings(
    workspace_id: int,
    payload: UpdateWorkspaceSettingsPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    workspace.name = payload.name.strip()
    workspace.description = (payload.description or "").strip() or None
    workspace.billing_email = (payload.billing_email or "").strip() or None
    workspace.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(workspace)

    return serialize_workspace_settings(workspace)
    


@router.get("/workspaces/{workspace_id}/usage")
def get_workspace_usage(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    entitlement = build_entitlement_snapshot(
        workspace_id,
        db,
    )

    # Defensive normalization layer
    if "usage" not in entitlement:
        entitlement["usage"] = {}

    if "limits" not in entitlement:
        entitlement["limits"] = {}

    if "metrics" not in entitlement:
        entitlement["metrics"] = {}

    trade_metrics = get_workspace_trade_metrics(
        db,
        workspace_id,
    )

    entitlement["usage"]["trades"] = (
        trade_metrics["used"]
    )

    entitlement["usage"]["active_trades"] = (
        trade_metrics["ledger_count"]
    )

    entitlement["limits"]["trades"] = (
        trade_metrics["limit"]
    )

    entitlement["trade_metrics"] = trade_metrics

    return entitlement


@router.get("/workspaces/{workspace_id}/members")
def list_workspace_members(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_member(workspace_id, current_user, db)

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    rows = (
        db.query(WorkspaceMembership, User)
        .join(User, User.id == WorkspaceMembership.user_id)
        .filter(WorkspaceMembership.workspace_id == workspace_id)
        .order_by(WorkspaceMembership.id.asc())
        .all()
    )

    return [serialize_workspace_member(membership, user) for membership, user in rows]


@router.patch("/workspaces/{workspace_id}/members/{user_id}")
def update_workspace_member_role(
    workspace_id: int,
    user_id: int,
    payload: UpdateWorkspaceMemberRolePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")

    target_role = normalize_workspace_role(payload.role)

    if membership.user_id == current_user.id and target_role != "owner":
        raise HTTPException(status_code=400, detail="Owner cannot demote themselves")

    if membership.role == "owner" and target_role != "owner":
        owner_count = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.role == "owner",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Workspace must retain at least one owner")

    old_role = membership.role
    membership.role = target_role
    db.commit()
    db.refresh(membership)

    log_audit_event(
        db,
        event_type="workspace_membership_role_updated",
        entity_type="workspace_membership",
        entity_id=membership.id,
        workspace_id=workspace_id,
        old_state={"role": old_role},
        new_state={"role": membership.role},
        metadata={
            "source": "workspaces.update_workspace_member_role",
            "actor_user_id": current_user.id,
            "target_user_id": user_id,
        },
    )

    user = db.query(User).filter(User.id == membership.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return serialize_workspace_member(membership, user)



class CreateWorkspaceInvitePayload(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    role: str = Field(default="member", min_length=1, max_length=50)


@router.get("/workspaces/{workspace_id}/invites")
def list_workspace_invites(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    invites = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id
        )
        .order_by(WorkspaceInvite.id.desc())
        .all()
    )

    return [
        {
            "id": invite.id,
            "email": invite.email,
            "role": invite.role,
            "status": invite.status,
            "token": invite.token,
            "created_at": (
                invite.created_at.isoformat()
                if invite.created_at
                else None
            ),
        }
        for invite in invites
    ]


@router.post("/workspaces/{workspace_id}/invites")
def create_workspace_invite(
    workspace_id: int,
    payload: CreateWorkspaceInvitePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id)
        .first()
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    require_workspace_owner(
        workspace_id,
        current_user,
        db,
    )

    normalized_email = payload.email.strip().lower()

    existing_invite = (
        db.query(WorkspaceInvite)
        .filter(
            WorkspaceInvite.workspace_id == workspace_id,
            WorkspaceInvite.email == normalized_email,
            WorkspaceInvite.status == "pending",
        )
        .first()
    )

    if existing_invite:
        return {
            "id": existing_invite.id,
            "email": existing_invite.email,
            "role": existing_invite.role,
            "status": existing_invite.status,
            "token": existing_invite.token,
        }

    invite = WorkspaceInvite(
        workspace_id=workspace_id,
        email=normalized_email,
        role=normalize_workspace_role(payload.role),
        token=token_urlsafe(24),
        status="pending",
        invited_by_user_id=current_user.id,
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    invite_link = (
        f"https://trading-truth-layer.vercel.app/invite/"
        f"{invite.token}"
    )

    return {
        "id": invite.id,
        "email": invite.email,
        "role": invite.role,
        "status": invite.status,
        "token": invite.token,
        "invite_link": invite_link,
    }


@router.delete("/workspaces/{workspace_id}/members/{user_id}")
def remove_workspace_member(
    workspace_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    require_workspace_owner(workspace_id, current_user, db)

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    membership = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace membership not found")

    if membership.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Owner cannot remove themselves from the workspace")

    if membership.role == "owner":
        owner_count = (
            db.query(WorkspaceMembership)
            .filter(
                WorkspaceMembership.workspace_id == workspace_id,
                WorkspaceMembership.role == "owner",
            )
            .count()
        )
        if owner_count <= 1:
            raise HTTPException(status_code=400, detail="Workspace must retain at least one owner")

    user = db.query(User).filter(User.id == membership.user_id).first()
    old_state = {
        "workspace_id": membership.workspace_id,
        "user_id": membership.user_id,
        "role": membership.role,
    }

    membership_id = membership.id
    db.delete(membership)
    db.commit()

    log_audit_event(
        db,
        event_type="workspace_member_removed",
        entity_type="workspace_membership",
        entity_id=membership_id,
        workspace_id=workspace_id,
        old_state=old_state,
        new_state=None,
        metadata={
            "source": "workspaces.remove_workspace_member",
            "actor_user_id": current_user.id,
            "target_user_id": user_id,
            "target_email": user.email if user else None,
        },
    )

    return {
        "removed": True,
        "workspace_id": workspace_id,
        "user_id": user_id,
    }


@router.get("/api/debug/whoami")
def debug_whoami(
    current_user: User = Depends(get_current_user),
):
    return {
        "user_id": current_user.id,
        "email": current_user.email,
    }