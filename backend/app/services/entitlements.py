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

PLAN_DEFAULTS = {

    "sandbox": {
        "is_public": True,
        "name": "Sandbox",
        "description": (
            "Controlled evaluation environment for product proof, "
            "limited governed capacity, and safe pre-billing exploration."
        ),
        "recommended_for": [
            "product evaluation",
            "proof of concept",
            "sandbox testing",
        ],
        "pricing": {
            "monthly": 0,
            "annual": 0,
        },
        "claims": 5,
        "trades": 1000,
        "members": 3,
        "storage_mb": 100,
        "infrastructure": [
            "Manual Trade Import",
            "Evidence Registry",
            "PDF Evidence Reports",
            "Workspace Governance",
            "Verification Ledger",
        ],

        "commercial_services": [
            "Manual Trade Imports",
            "CSV Import",
            "Claim Verification",
            "Evidence Registry",
            "Workspace Management",
        ],

        "capacity_summary": {
            "claims": "5 Claims",
            "trades": "1,000 Trades",
            "members": "3 Members",
            "storage": "100 MB",
        },
    },

    "internal": {
        "is_public": False,
        "name": "Internal",
        "description": (
            "Internal unrestricted owner workspace."
        ),
        "recommended_for": [
            "platform ownership",
            "internal operations",
        ],
        "pricing": {
            "monthly": 0,
            "annual": 0,
        },
        "claims": 999999999,
        "trades": 999999999,
        "members": 999999999,
        "storage_mb": 999999999,
    },

    "starter": {
        "is_public": True,
        "name": "Starter",
        "description": (
            "Commercial onboarding tier for independent verification "
            "workflows and governed claim operations."
        ),
        "recommended_for": [
            "independent traders",
            "solo verification",
            "small governance workflows",
        ],
        "pricing": {
            "monthly": 19,
            "annual": 190,
        },
        "claims": 5,
        "trades": 5000,
        "members": 3,
        "storage_mb": 500,
        "infrastructure": [
            "Public Verification",
            "Claim Governance",
            "Trust Registry",
            "Verification Links",
            "Evidence Export",
        ],

        "commercial_services": [
            "Everything in Sandbox",
            "Public Verification Pages",
            "Verification Links",
            "Trust Directory",
            "Workspace Governance",
        ],

        "capacity_summary": {
            "claims": "5 Claims",
            "trades": "5,000 Trades",
            "members": "3 Members",
            "storage": "500 MB",
        },
    },

    "pro": {
        "is_public": True,
        "name": "Pro",
        "description": (
            "Expanded governed infrastructure for active verification, "
            "broker ingestion, and operational continuity."
        ),
        "recommended_for": [
            "professional traders",
            "active verification",
            "broker integrations",
        ],
        "pricing": {
            "monthly": 79,
            "annual": 790,
        },
        "claims": 50,
        "trades": 50000,
        "members": 25,
        "storage_mb": 2048,
        "infrastructure": [
            "Broker Connectivity",
            "Verification Intelligence",
            "Institutional Reports",
            "Trust Analytics",
            "Verification Network",
        ],

        "commercial_services": [
            "Everything in Starter",
            "Broker Connections",
            "Verification Analytics",
            "Trust Intelligence",
            "Verification Network",
        ],

        "capacity_summary": {
            "claims": "50 Claims",
            "trades": "50,000 Trades",
            "members": "25 Members",
            "storage": "2 GB",
        },
    },

    "growth": {
        "is_public": True,
        "name": "Growth",
        "description": (
            "Scaled operational trust infrastructure for growing "
            "teams, external verification, and API-connected workflows."
        ),
        "recommended_for": [
            "growing organizations",
            "API verification",
            "team governance",
        ],
        "pricing": {
            "monthly": 249,
            "annual": 2490,
        },
        "claims": 200,
        "trades": 250000,
        "members": 100,
        "storage_mb": 10240,
        "infrastructure": [
            "Continuous Synchronization",
            "Automation Engine",
            "External API",
            "Evidence Analytics",
            "Operational Governance",
        ],

        "commercial_services": [
            "Everything in Pro",
            "Continuous Sync",
            "Automation",
            "External API",
            "Evidence Analytics",
        ],

        "capacity_summary": {
            "claims": "200 Claims",
            "trades": "250,000 Trades",
            "members": "100 Members",
            "storage": "10 GB",
        },
    },

    "business": {
        "is_public": True,
        "name": "Business",
        "description": (
            "Enterprise-scale governance and verification capacity "
            "for institutional trust infrastructure."
        ),
        "recommended_for": [
            "institutions",
            "enterprise verification",
            "large governance operations",
        ],
        "pricing": {
            "monthly": 999,
            "annual": 9990,
        },
        "claims": 500,
        "trades": 1000000,
        "members": 250,
        "storage_mb": 51200,
        "infrastructure": [
            "Enterprise Governance",
            "Institutional API",
            "Dedicated Infrastructure",
            "Compliance Reports",
            "Priority Support",
        ],

        "commercial_services": [
            "Everything in Growth",
            "Enterprise Governance",
            "Institutional Reports",
            "Dedicated Infrastructure",
            "Priority Support",
        ],

        "capacity_summary": {
            "claims": "500 Claims",
            "trades": "1,000,000 Trades",
            "members": "250 Members",
            "storage": "50 GB",
        },
    },
}


PLAN_FEATURES = {

    "sandbox": {

        "manual_trades": True,
        "csv_import": True,

        "broker_connections": False,
        "continuous_sync": False,

        "claim_lifecycle": True,
        "verification_routes": False,
        "public_records": False,
        "verification_network": False,

        "pdf_reports": True,
        "json_export": True,
        "zip_export": False,

        "external_review": False,
        "trust_intelligence": False,
        "evidence_analytics": False,
        "api_access": False,

        "multi_user": False,

    },

    "starter": {

        "manual_trades": True,
        "csv_import": True,

        "broker_connections": False,
        "continuous_sync": False,

        "claim_lifecycle": True,
        "verification_routes": True,
        "public_records": True,
        "verification_network": False,

        "pdf_reports": True,
        "json_export": True,
        "zip_export": True,

        "external_review": False,
        "trust_intelligence": False,
        "evidence_analytics": False,
        "api_access": False,

        "multi_user": False,

    },

    "pro": {

        "manual_trades": True,
        "csv_import": True,

        "broker_connections": True,
        "continuous_sync": False,

        "claim_lifecycle": True,
        "verification_routes": True,
        "public_records": True,
        "verification_network": True,

        "pdf_reports": True,
        "json_export": True,
        "zip_export": True,

        "external_review": False,
        "trust_intelligence": True,
        "evidence_analytics": False,
        "api_access": False,

        "multi_user": False,

    },

    "growth": {

        "manual_trades": True,
        "csv_import": True,

        "broker_connections": True,
        "continuous_sync": True,

        "claim_lifecycle": True,
        "verification_routes": True,
        "public_records": True,
        "verification_network": True,

        "pdf_reports": True,
        "json_export": True,
        "zip_export": True,

        "external_review": True,
        "trust_intelligence": True,
        "evidence_analytics": True,
        "api_access": True,

        "multi_user": True,

    },

    "business": {

        "manual_trades": True,
        "csv_import": True,

        "broker_connections": True,
        "continuous_sync": True,

        "claim_lifecycle": True,
        "verification_routes": True,
        "public_records": True,
        "verification_network": True,

        "pdf_reports": True,
        "json_export": True,
        "zip_export": True,

        "external_review": True,
        "trust_intelligence": True,
        "evidence_analytics": True,
        "api_access": True,

        "multi_user": True,

        "allocator_workflows": True,
        "institutional_reports": True,
        "audit_exports": True,

    },

    "internal": {

        "__all__": True,

    }

}


PLAN_COMMERCIAL_SERVICES = {
    "sandbox": [
        "Manual Trade Imports",
        "CSV Import",
        "Claim Lifecycle",
        "PDF Evidence Reports",
        "JSON Export",
    ],

    "starter": [
        "Everything in Sandbox",
        "Public Verification Pages",
        "Public Records",
        "ZIP Evidence Export",
        "Verification Governance",
    ],

    "pro": [
        "Everything in Starter",
        "Broker Connections",
        "Verification Network",
        "Trust Intelligence",
        "Professional Verification Infrastructure",
    ],

    "growth": [
        "Everything in Pro",
        "Continuous Broker Synchronization",
        "Evidence Analytics",
        "External Review",
        "API Access",
        "Multi-user Workspace",
    ],

    "business": [
        "Everything in Growth",
        "Institutional Reports",
        "Allocator Workflows",
        "Audit Exports",
        "Enterprise Governance",
    ],

    "internal": [
        "All Commercial Services",
        "Unlimited Internal Access",
    ],
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


def get_workspace_plan_features(
    workspace: Workspace,
) -> dict[str, Any]:

    plan = resolve_workspace_plan_code(
        workspace
    )

    features = PLAN_FEATURES.get(
        plan,
        {},
    )

    if features.get("__all__"):

        return {
            "__all__": True
        }

    return features.copy()


def workspace_has_feature(
    workspace: Workspace,
    feature: str,
) -> bool:

    features = get_workspace_plan_features(
        workspace
    )

    if features.get("__all__"):

        return True

    return bool(
        features.get(
            feature,
            False,
        )
    )


def enforce_workspace_feature(

    workspace_id: int,

    db: Session,

    feature: str,

    action: str,

) -> Workspace:

    workspace = enforce_workspace_billing_access(

        workspace_id,

        db,

        allow_past_due=True,

        action_label=action,

    )

    if workspace_has_feature(
        workspace,
        feature,
    ):
        return workspace

    raise HTTPException(

        status_code=403,

        detail={

            "code": "feature_locked",

            "feature": feature,

            "plan": resolve_workspace_plan_code(
                workspace
            ),

            "upgrade_required": True,

            "message":

                f"{feature.replace('_',' ').title()} requires a higher workspace plan.",

        },

    )


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
        "ledger_trades": active_trade_count,

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

    live_trade_count = usage.get("ledger_trades", 0)

    immutable_trade_usage = usage.get("trades", 0)

    governed_trade_usage = max(
        live_trade_count,
        immutable_trade_usage,
    )
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
        "features": get_workspace_plan_features(workspace),

        "commercial_services":
            PLAN_COMMERCIAL_SERVICES.get(
                resolved_plan_code,
                []
            ),
        "usage": {
            "members": usage["members"],

            # GOVERNED TRADE USAGE
            "trades": governed_trade_usage,

            # LIVE LEDGER ROWS
            "active_trades": live_trade_count,

            "claims": usage["claims"],

            "storage_mb": usage["storage_mb"],
        },
        "metrics": {
            "used": governed_trade_usage,

            "consumed": immutable_trade_usage,

            "ledger_count": live_trade_count,

            "removed_trades": max(
                immutable_trade_usage
                - live_trade_count,
                0,
            ),

            "limit": limits["trades"],

            "utilization": (
                round(
                    (
                        governed_trade_usage
                        / limits["trades"]
                    ) * 100,
                    2,
                )
                if limits["trades"] > 0
                else 0
            ),
        },
        "diagnostics": {
            "resolved_plan_code": resolved_plan_code,
            "raw_limit_columns": get_workspace_raw_limit_columns(workspace),
            "defaults_for_resolved_plan": PLAN_DEFAULTS[resolved_plan_code],
        },
        "available_plans": [
            {
                "code": code,
                "name": PLAN_DEFAULTS[code]["name"],
                "description": PLAN_DEFAULTS[code]["description"],
                "pricing": PLAN_DEFAULTS[code]["pricing"],
                "recommended_for": PLAN_DEFAULTS[code]["recommended_for"],
                "commercial_services": PLAN_COMMERCIAL_SERVICES.get(code, []),
                "features": PLAN_FEATURES.get(code, {}),
            }
            for code in get_public_plan_codes()
        ],
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