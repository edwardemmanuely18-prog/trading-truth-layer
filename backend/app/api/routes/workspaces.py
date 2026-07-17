from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.import_job import ImportJob
from app.models.sync_job import SyncJob

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.claim_schema import ClaimSchema
from app.models.trade import Trade
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_preferences import (
    WorkspacePreferences,
)
from app.models.broker_connection import BrokerConnection
from app.models.broker_adapter import BrokerAdapter
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

from app.models.broker_credential import (
    BrokerCredential,
)

from app.services.broker_verification_service import (
    verify_connection,
)

from app.models.broker_account import (
    BrokerAccount,
)

from app.services.plan_simulation import (
    PlanSimulationService,
)

from app.services.authorization.registry.capability_catalog import (
    SETTINGS_UPDATE,
)

from app.api.authorization_deps import (
    require_workspace_context,
)

from app.services.authorization.engine.authorization_service import (
    AuthorizationService,
)

from app.services.authorization.registry.capability_catalog import (
    BROKER_CONNECTION_READ,
    BROKER_CONNECTION_WRITE,
    EVIDENCE_IMPORT,
)

from app.services.entitlements import (
    enforce_workspace_page_access,
)


from secrets import token_urlsafe

from app.models.workspace_invite import WorkspaceInvite

from fastapi import UploadFile, File, Form


router = APIRouter()



class CreateBrokerConnectionRequest(BaseModel):
    provider: str
    connection_name: str


class VerifyBrokerConnectionRequest(
    BaseModel
):
    connection_id: int

    login: str | None = None
    password: str | None = None
    server: str | None = None

    host: str | None = None
    port: int | None = None
    client_id: int | None = None

    flex_query_id: str | None = None
    flex_token: str | None = None


class ExecuteSyncRequest(BaseModel):
    sync_job_id: int


class CreateWorkspacePayload(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class UpdateWorkspaceSettingsPayload(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    billing_email: str | None = Field(
        default=None,
        max_length=255,
    )

    timezone: str = "UTC"

    language: str = "English"

    currency: str = "USD"

    date_format: str = "YYYY-MM-DD"

    auto_refresh: bool = True

    auto_save: bool = True


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

        # --------------------------------------------------
        # Settings Page Extensions
        # --------------------------------------------------

        "preferences": None,

        "profile": {

            "workspace_name": workspace.name,

            "description": workspace.description,

            "billing_email": workspace.billing_email,

        },

        "branding": None,

        "verification_preferences": None,

        "governance": None,

        "billing_summary": None,

        "platform_readiness": None,

        # --------------------------------------------------
        # Billing Page Compatibility
        # --------------------------------------------------

        "configured_plan": normalize_plan_code(
            workspace.plan_code
        ),

        "effective_plan": resolve_workspace_plan_code(
            workspace
        ),

        # --------------------------------------------------
        # Plan Simulation Compatibility
        # --------------------------------------------------

        "is_internal": bool(
            getattr(
                workspace,
                "is_internal_workspace",
                False,
            )
        ),

        "effective_plan_code":
            resolve_workspace_plan_code(
                workspace
            ),

        "effective_plan_detail": None,

        "effective_limits": {

            "claim_limit":
                limits.get(
                    "claims",
                    0,
                ),

            "trade_limit":
                limits.get(
                    "trades",
                    0,
                ),

            "member_limit":
                limits.get(
                    "members",
                    0,
                ),

            "storage_limit_mb":
                limits.get(
                    "storage_mb",
                    0,
                ),

        },

        "plan_governance": {

            "configured_plan_code":
                normalize_plan_code(
                    workspace.plan_code
                ),

            "effective_plan_code":
                resolve_workspace_plan_code(
                    workspace
                ),

            "billing_status":
                normalize_billing_status(
                    workspace.billing_status
                ),

            "paid_access_active":
                True,

            "plan_mismatch":
                False,

            "reason":
                "internal",

            "message":
                "Internal workspace plan.",

        },

        "billing_provider": (
            workspace.billing_provider
            or "manual"
        ),

        "billing_status": normalize_billing_status(
            workspace.billing_status
        ),

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

    context = Depends(
        require_workspace_context(
            "dashboard",
        )
    ),
):
    workspace = context.workspace

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


@router.get(
    "/workspaces/{workspace_id}/snapshot"
)
def get_workspace_snapshot(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),

    context = Depends(
        require_workspace_context(
            "dashboard",
        )
    ),
):
    workspace = context.workspace

    trade_count = (
        db.query(Trade)
        .filter(
            Trade.workspace_id == workspace_id
        )
        .count()
    )

    claim_count = (
        db.query(ClaimSchema)
        .filter(
            ClaimSchema.workspace_id == workspace_id
        )
        .count()
    )

    member_count = (
        db.query(WorkspaceMembership)
        .filter(
            WorkspaceMembership.workspace_id == workspace_id
        )
        .count()
    )

    return {
        "workspace_id": workspace.id,
        "workspace_name": workspace.name,
        "trade_count": trade_count,
        "claim_count": claim_count,
        "member_count": member_count,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/workspaces/{workspace_id}/settings")
def get_workspace_settings(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),

    context = Depends(
        require_workspace_context(
            "settings",
        )
    ),
):
    workspace = context.workspace

    settings = serialize_workspace_settings(workspace)

    preferences = (
        db.query(WorkspacePreferences)
        .filter(
            WorkspacePreferences.workspace_id == workspace.id
        )
        .first()
    )

    if preferences:

        settings["preferences"] = {

            "timezone": preferences.timezone,

            "language": preferences.language,

            "currency": preferences.currency,

            "date_format": preferences.date_format,

            "auto_refresh": preferences.auto_refresh,

            "auto_save": preferences.auto_save,

        }

    else:

        settings["preferences"] = {

            "timezone": "UTC",

            "language": "English",

            "currency": "USD",

            "date_format": "YYYY-MM-DD",

            "auto_refresh": True,

            "auto_save": True,

        }

    settings["billing"] = {
        "provider": (
            workspace.billing_provider
            or "manual"
        ),
        "status": normalize_billing_status(
            workspace.billing_status
        ),
        "configured_plan": normalize_plan_code(
            workspace.plan_code
        ),
        "effective_plan": resolve_workspace_plan_code(
            workspace
        ),
    }

    return settings


@router.patch("/workspaces/{workspace_id}/settings")
def update_workspace_settings(
    workspace_id: int,
    payload: UpdateWorkspaceSettingsPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),

    context = Depends(
        require_workspace_context(
            "settings",
        )
    ),
):
    workspace = context.workspace

    AuthorizationService.require_capability(
        context.access,
        SETTINGS_UPDATE,
    )

    workspace.name = payload.name.strip()
    workspace.description = (payload.description or "").strip() or None
    workspace.billing_email = (payload.billing_email or "").strip() or None

    preferences = (
        db.query(WorkspacePreferences)
        .filter(
            WorkspacePreferences.workspace_id == workspace.id
        )
        .first()
    )

    if preferences is None:

        preferences = WorkspacePreferences(
            workspace_id=workspace.id,
        )

        db.add(preferences)

    preferences.timezone = payload.timezone

    preferences.language = payload.language

    preferences.currency = payload.currency

    preferences.date_format = payload.date_format

    preferences.auto_refresh = payload.auto_refresh

    preferences.auto_save = payload.auto_save

    workspace.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(workspace)

    settings = serialize_workspace_settings(workspace)

    settings["preferences"] = {

        "timezone": preferences.timezone,

        "language": preferences.language,

        "currency": preferences.currency,

        "date_format": preferences.date_format,

        "auto_refresh": preferences.auto_refresh,

        "auto_save": preferences.auto_save,

    }

    settings["billing"] = {
        "provider": (
            workspace.billing_provider
            or "manual"
        ),
        "status": normalize_billing_status(
            workspace.billing_status
        ),
        "configured_plan": normalize_plan_code(
            workspace.plan_code
        ),
        "effective_plan": resolve_workspace_plan_code(
            workspace
        ),
    }

    return settings
    


@router.get("/workspaces/{workspace_id}/usage")
def get_workspace_usage(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),

    context = Depends(
        require_workspace_context(
            "billing",
        )
    ),
):
    workspace = context.workspace

    entitlement = build_entitlement_snapshot(
        workspace_id,
        db,
    )

    entitlement["commercial_services"] = entitlement.get(
        "commercial_services",
        {}
    )

    entitlement["features"] = entitlement.get(
        "features",
        {}
    )

    entitlement["permissions"] = entitlement.get(
        "permissions",
        {}
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

    # ---------------------------------------------------
    # Billing Page Compatibility
    # ---------------------------------------------------

    entitlement["configured_plan"] = normalize_plan_code(
        workspace.plan_code
    )

    entitlement["effective_plan"] = resolve_workspace_plan_code(
        workspace
    )

    entitlement["billing_status"] = normalize_billing_status(
        workspace.billing_status
    )

    return entitlement


@router.get("/workspaces/{workspace_id}/entitlements")
def get_workspace_entitlements(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),

    context = Depends(
        require_workspace_context(
            "billing",
        )
    ),
):
    workspace = context.workspace

    entitlement = build_entitlement_snapshot(
        workspace_id,
        db,
    )

    entitlement["configured_plan"] = normalize_plan_code(
        workspace.plan_code
    )

    entitlement["effective_plan"] = (
        resolve_workspace_plan_code(workspace)
    )

    entitlement["billing_status"] = (
        normalize_billing_status(
            workspace.billing_status
        )
    )

    return entitlement


from pydantic import BaseModel


class PlanSimulationRequest(BaseModel):

    plan: str


import os


def ensure_plan_simulation_enabled(
    workspace: Workspace,
):
    """
    Production safety.

    Plan Simulation is only available when explicitly enabled
    and only inside internal workspaces.
    """

    if (
        os.getenv(
            "ENABLE_PLAN_SIMULATION",
            "false",
        ).lower()
        != "true"
    ):
        raise HTTPException(
            status_code=404,
            detail="Not Found",
        )

    if not getattr(
        workspace,
        "is_internal_workspace",
        False,
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Plan simulation is restricted "
                "to internal workspaces."
            ),
        )


@router.get(
    "/workspaces/{workspace_id}/plan-simulation"
)
def get_plan_simulation(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    ensure_plan_simulation_enabled(
        workspace,
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

    return PlanSimulationService.build_snapshot(
        workspace,
    )


@router.put(
    "/workspaces/{workspace_id}/plan-simulation"
)
def update_plan_simulation(
    workspace_id: int,
    request: PlanSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if workspace is None:

        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    ensure_plan_simulation_enabled(
        workspace,
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

    PlanSimulationService.set_override(

        workspace_id,

        request.plan,

    )

    return PlanSimulationService.build_snapshot(
        workspace,
    )


@router.delete(
    "/workspaces/{workspace_id}/plan-simulation"
)
def clear_plan_simulation(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
        .first()
    )

    if workspace is None:

        raise HTTPException(
            status_code=404,
            detail="Workspace not found",
        )

    ensure_plan_simulation_enabled(
        workspace,
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

    PlanSimulationService.clear_override(
        workspace_id,
    )

    return PlanSimulationService.build_snapshot(
        workspace,
    )


@router.get("/workspaces/{workspace_id}/governance")
def get_workspace_governance(
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

    return {
        "workspace_id": workspace.id,

        "configured_plan": normalize_plan_code(
            workspace.plan_code
        ),

        "effective_plan": resolve_workspace_plan_code(
            workspace
        ),

        "billing_status": normalize_billing_status(
            workspace.billing_status
        ),

        "billing_provider": (
            workspace.billing_provider
            or "manual"
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

        "workspace_locked": False,

        "verification_locked": False,

        "claim_lock_enabled": True,

        "publish_enabled": True,

        "owner_required": True,
    }


@router.get("/workspaces/{workspace_id}/broker-connections")
def list_broker_connections(
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

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_READ,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="access Broker Connections",
    )

    enforce_internal_workspace_access(
        workspace,
        current_user,
        db,
    )

    connections = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.workspace_id == workspace_id
        )
        .order_by(BrokerConnection.id.desc())
        .all()
    )

    return [
        {
            "id": row.id,
            "workspace_id": row.workspace_id,
            "provider": row.provider,
            "connection_name": row.connection_name,
            "account_id": row.account_id,
            "account_name": row.account_name,
            "adapter_type": row.adapter_type,
            "sync_mode": row.sync_mode,
            "connection_status": row.connection_status,
            "sync_status": row.sync_status,
            "verification_status": row.verification_status,
            "trust_tier": row.trust_tier,
            "last_sync_error": row.last_sync_error,
            "last_sync_at": (
                row.last_sync_at.isoformat()
                if row.last_sync_at
                else None
            ),
            "verified_at": (
                row.verified_at.isoformat()
                if row.verified_at
                else None
            ),
            "created_at": (
                row.created_at.isoformat()
                if row.created_at
                else None
            ),
            "account_environment":
                row.account_environment,
        }
        for row in connections
    ]


@router.post(
    "/workspaces/{workspace_id}/broker-connections"
)
def create_broker_connection(
    workspace_id: int,
    payload: CreateBrokerConnectionRequest,
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

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_WRITE,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="create Broker Connection",
    )

    adapter = (
        db.query(BrokerAdapter)
        .filter(
            BrokerAdapter.provider == payload.provider
        )
        .first()
    )

    if not adapter:
        raise HTTPException(
            status_code=404,
            detail="Adapter not found",
        )

    connection = BrokerConnection(
        workspace_id=workspace_id,
        provider=payload.provider,
        connection_name=payload.connection_name,
        adapter_type=adapter.adapter_type,
        trust_tier=adapter.trust_tier,
        connection_status="pending",
        sync_status="idle",
        verification_status="pending",
        account_environment="unknown",
    )

    db.add(connection)
    db.commit()
    db.refresh(connection)

    return {
        "id": connection.id,
        "provider": connection.provider,
        "connection_name": connection.connection_name,
        "connection_status": connection.connection_status,
        "verification_status": connection.verification_status,
        "trust_tier": connection.trust_tier,
    }


@router.post(
    "/workspaces/{workspace_id}/broker-connections/verify"
)
def verify_broker_connection(
    workspace_id: int,
    payload: VerifyBrokerConnectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_WRITE,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="verify Broker Connection",
    )

    connection = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.id
            == payload.connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Connection not found",
        )

    result = verify_connection(
        connection.provider,
        payload.model_dump(),
    )

    if not result["success"]:

        connection.connection_status = (
            "verification_failed"
        )

        db.commit()

        raise HTTPException(
            status_code=400,
            detail=result["error"],
        )

    existing_credential = (
        db.query(BrokerCredential)
        .filter(
            BrokerCredential.connection_id
            == connection.id
        )
        .first()
    )

    if connection.provider in [
        "interactive_brokers",
        "ibkr",
    ]:

        if existing_credential:

            existing_credential.host = payload.host

            existing_credential.port = payload.port

            existing_credential.client_id = payload.client_id

            existing_credential.flex_enabled = bool(
                payload.flex_query_id
                and payload.flex_token
            )

            existing_credential.flex_query_id = (
                payload.flex_query_id
            )

            existing_credential.flex_token_encrypted = (
                payload.flex_token
            )

        else:

            credential = BrokerCredential(
                connection_id=connection.id,
                credential_type="ibkr_gateway",

                host=payload.host,

                port=payload.port,

                client_id=payload.client_id,

                flex_enabled=bool(
                    payload.flex_query_id
                    and payload.flex_token
                ),

                flex_query_id=payload.flex_query_id,

                flex_token_encrypted=(
                    payload.flex_token
                ),
            )

            db.add(credential)

    else:

        if existing_credential:

            existing_credential.username = (
                payload.login
            )

            existing_credential.password_encrypted = (
                payload.password
            )

            existing_credential.server_name = (
                payload.server
            )

        else:

            credential = BrokerCredential(
                connection_id=connection.id,
                credential_type="broker_login",

                username=payload.login,

                password_encrypted=payload.password,

                server_name=payload.server,
            )

            db.add(credential)

    connection.account_id = (
        result["account_id"]
    )

    connection.account_name = (
        result["account_name"]
    )

    connection.account_environment = (
        result["account_environment"]
    )

    connection.broker_account_id = (
        result.get("broker_account_id")
    )

    connection.broker_server = (
        result.get("broker_server")
    )

    connection.broker_currency = (
        result.get("currency")
    )

    connection.broker_leverage = (
        result.get("leverage")
    )

    connection.account_balance = (
        result.get("balance")
    )

    connection.account_equity = (
        result.get("equity")
    )

    connection.connection_status = (
        "connected"
    )

    connection.verification_status = (
        "verified"
    )

    connection.verified_at = datetime.utcnow()

    db.commit()

    return {
        "success": True,
        "connection_id":
            connection.id,

        "account_id":
            connection.account_id,

        "account_name":
            connection.account_name,

        "environment":
            connection.account_environment,

        "broker_account_id":
            connection.broker_account_id,

        "broker_server":
            connection.broker_server,

        "currency":
            connection.broker_currency,

        "balance":
            connection.account_balance,

        "equity":
            connection.account_equity,
    }


@router.post(
    "/workspaces/{workspace_id}/broker-connections/{connection_id}/discover-accounts"
)
def discover_broker_accounts(
    workspace_id: int,
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_WRITE,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="discover Broker Accounts",
    )

    connection = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.id
            == connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Connection not found",
        )

    credential = (
        db.query(BrokerCredential)
        .filter(
            BrokerCredential.connection_id
            == connection.id
        )
        .first()
    )

    if not credential:
        raise HTTPException(
            status_code=400,
            detail="Credential missing",
        )

    from app.services.broker_connector_factory import (
        get_connector,
    )

    connector = get_connector(
        connection.provider,
        credential,
    )

    accounts = (
        connector.discover_accounts()
    )

    db.query(BrokerAccount).filter(
        BrokerAccount.connection_id
        == connection.id
    ).delete()

    db.flush()

    created = []

    for account in accounts:

        row = BrokerAccount(
            connection_id=
                connection.id,

            broker_account_id=
                account.account_id,

            account_name=
                account.account_name,

            environment=
                account.environment,

            currency=
                account.currency,
        )

        db.add(row)

        created.append(
            account.account_id
        )

    db.commit()

    return {
        "success": True,
        "accounts_discovered":
            len(created),
    }


@router.get(
    "/workspaces/{workspace_id}/broker-connections/{connection_id}/accounts"
)
def list_discovered_accounts(
    workspace_id: int,
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_READ,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="view Broker Accounts",
    )

    rows = (
        db.query(BrokerAccount)
        .filter(
            BrokerAccount.connection_id
            == connection_id
        )
        .all()
    )

    return [
        {
            "id": row.id,
            "broker_account_id":
                row.broker_account_id,
            "account_name":
                row.account_name,
            "environment":
                row.environment,
            "currency":
                row.currency,
        }
        for row in rows
    ]


@router.get(
    "/workspaces/{workspace_id}/broker-adapters"
)
def list_broker_adapters(
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

    adapters = (
        db.query(BrokerAdapter)
        .order_by(BrokerAdapter.display_name)
        .all()
    )

    return [
        {
            "id": adapter.id,
            "provider": adapter.provider,
            "display_name": adapter.display_name,
            "adapter_type": adapter.adapter_type,
            "trust_tier": adapter.trust_tier,
            "supports_live_sync": adapter.supports_live_sync,
            "supports_historical_import": adapter.supports_historical_import,
            "status": adapter.status,
        }
        for adapter in adapters
    ]


@router.get(
    "/workspaces/{workspace_id}/import-jobs"
)
def list_import_jobs(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
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

    jobs = (
        db.query(ImportJob)
        .filter(
            ImportJob.workspace_id
            == workspace_id
        )
        .order_by(
            ImportJob.id.desc()
        )
        .all()
    )

    return [
        {
            "id": job.id,
            "adapter_provider":
                job.adapter_provider,
            "filename":
                job.filename,
            "file_type":
                job.file_type,
            "status":
                job.status,
            "records_detected":
                job.records_detected,
            "imported_records":
                job.imported_records,
            "created_at":
                job.created_at.isoformat(),
        }
        for job in jobs
    ]


@router.get(
    "/workspaces/{workspace_id}/sync-jobs"
)
def list_sync_jobs(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_READ,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="view Sync Jobs",
    )

    jobs = (
        db.query(SyncJob)
        .filter(
            SyncJob.workspace_id
            == workspace_id
        )
        .order_by(
            SyncJob.id.desc()
        )
        .all()
    )

    return [
        {
            "id": job.id,
            "provider": job.provider,
            "sync_type": job.sync_type,
            "status": job.status,
            "records_processed":
                job.records_processed,
            "records_imported":
                job.records_imported,
            "records_skipped":
                getattr(
                    job,
                    "records_skipped",
                    0,
                ),
            "error_message":
                job.error_message,
            "started_at":
                job.started_at.isoformat()
                if job.started_at
                else None,
            "completed_at":
                job.completed_at.isoformat()
                if job.completed_at
                else None,
            "created_at":
                job.created_at.isoformat(),
        }
        for job in jobs
    ]


class CreateSyncJobRequest(
    BaseModel
):
    connection_id: int

    sync_type: str = (
        "incremental"
    )


@router.post(
    "/workspaces/{workspace_id}/sync-jobs"
)
def create_sync_job(
    workspace_id: int,
    payload: CreateSyncJobRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_WRITE,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="create Sync Job",
    )

    connection = (
        db.query(BrokerConnection)
        .filter(
            BrokerConnection.id
            == payload.connection_id
        )
        .first()
    )

    if not connection:
        raise HTTPException(
            status_code=404,
            detail="Connection not found",
        )

    if connection.connection_status != "connected":
        raise HTTPException(
            status_code=400,
            detail="Broker connection not verified",
        )

    allowed_sync_types = [
        "historical",
        "incremental",
        "positions",
        "account_state",
        "reconciliation",
    ]

    if payload.sync_type not in allowed_sync_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid sync type",
        )

    job = SyncJob(
        workspace_id=workspace_id,
        connection_id=
            payload.connection_id,
        provider=
            connection.provider,
        sync_type=
            payload.sync_type,
        status="queued",
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "success": True,
        "job_id": job.id,
    }


@router.post(
    "/workspaces/{workspace_id}/sync-jobs/{job_id}/execute"
)
def execute_sync_job_route(
    workspace_id: int,
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    require_workspace_member(
        workspace_id,
        current_user,
        db,
    )

    context = require_workspace_context(
        "broker_connections",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        BROKER_CONNECTION_WRITE,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="broker_connections",
        action="execute Sync Job",
    )

    from app.services.trade_import.sync_executor import (
        execute_sync_job,
    )

    result = execute_sync_job(
        db,
        job_id,
    )

    return {
        "success": True,
        "result": result,
    }


@router.post(
    "/workspaces/{workspace_id}/import-jobs"
)
async def create_import_job(
    workspace_id: int,
    adapter_provider: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(
            Workspace.id == workspace_id
        )
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

    context = require_workspace_context(
        "import_center",
    )(
        workspace_id=workspace_id,
        db=db,
        current_user=current_user,
    )

    AuthorizationService.require_capability(
        context.access,
        EVIDENCE_IMPORT,
    )

    enforce_workspace_page_access(
        workspace_id=workspace_id,
        db=db,
        page="import_center",
        action="upload import file",
    )

    job = ImportJob(
        workspace_id=workspace_id,
        adapter_provider=
            adapter_provider,
        filename=file.filename,
        file_type=file.content_type
            or "unknown",
        status="uploaded",
        records_detected=0,
        imported_records=0,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return {
        "success": True,
        "job_id": job.id,
    }


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

    