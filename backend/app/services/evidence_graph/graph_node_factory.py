"""
Trading Truth Layer (TTL)
Institutional Evidence Graph Engine

Canonical Graph Node Factory

Every node appearing inside the Evidence Graph MUST be
constructed through this module.

Never manually create node dictionaries elsewhere.
"""

from datetime import datetime
from typing import Any, Dict, Optional


#
# ----------------------------------------------------------------------
# Canonical Node Types
# ----------------------------------------------------------------------
#

NODE_CLAIM = "CLAIM"

NODE_CLAIM_SCHEMA = "CLAIM_SCHEMA"

NODE_TRADE = "TRADE"

NODE_IMPORT_BATCH = "IMPORT_BATCH"

NODE_BROKER_CONNECTION = "BROKER_CONNECTION"

NODE_BROKER_ACCOUNT = "BROKER_ACCOUNT"

NODE_ACCOUNT_SNAPSHOT = "ACCOUNT_SNAPSHOT"

NODE_AUDIT_EVENT = "AUDIT_EVENT"

NODE_INTEGRITY_ALERT = "INTEGRITY_ALERT"

NODE_INTEGRITY_SCAN = "INTEGRITY_SCAN"

NODE_REVIEW = "REVIEW"

NODE_DISPUTE = "DISPUTE"

NODE_PUBLIC_RECORD = "PUBLIC_RECORD"

NODE_PROVENANCE = "PROVENANCE"

NODE_INTEGRITY = "INTEGRITY"

NODE_RISK = "RISK"

NODE_METADATA = "METADATA"

NODE_WORKSPACE = "WORKSPACE"


#
# ----------------------------------------------------------------------
# Canonical Colors
# ----------------------------------------------------------------------
#

NODE_COLORS = {

    NODE_CLAIM:
        "#2563EB",

    NODE_CLAIM_SCHEMA:
        "#1D4ED8",

    NODE_TRADE:
        "#059669",

    NODE_IMPORT_BATCH:
        "#06B6D4",

    NODE_BROKER_CONNECTION:
        "#16A34A",

    NODE_BROKER_ACCOUNT:
        "#22C55E",

    NODE_ACCOUNT_SNAPSHOT:
        "#65A30D",

    NODE_AUDIT_EVENT:
        "#7C3AED",

    NODE_INTEGRITY_ALERT:
        "#DC2626",

    NODE_INTEGRITY_SCAN:
        "#F59E0B",

    NODE_REVIEW:
        "#6366F1",

    NODE_DISPUTE:
        "#EF4444",

    NODE_PUBLIC_RECORD:
        "#0284C7",

    NODE_PROVENANCE:
        "#0EA5E9",

    NODE_INTEGRITY:
        "#FACC15",

    NODE_RISK:
        "#B91C1C",

    NODE_METADATA:
        "#6B7280",

    NODE_WORKSPACE:
        "#334155",
}


#
# ----------------------------------------------------------------------
# Default Icons
# ----------------------------------------------------------------------
#

NODE_ICONS = {

    NODE_CLAIM:
        "shield",

    NODE_TRADE:
        "activity",

    NODE_IMPORT_BATCH:
        "database",

    NODE_BROKER_CONNECTION:
        "plug",

    NODE_BROKER_ACCOUNT:
        "wallet",

    NODE_ACCOUNT_SNAPSHOT:
        "camera",

    NODE_AUDIT_EVENT:
        "clipboard",

    NODE_INTEGRITY_ALERT:
        "triangle-alert",

    NODE_INTEGRITY_SCAN:
        "scan",

    NODE_PROVENANCE:
        "git-branch",

    NODE_INTEGRITY:
        "shield-check",

    NODE_RISK:
        "alert-octagon",

    NODE_METADATA:
        "info",

    NODE_WORKSPACE:
        "building",
}


#
# ----------------------------------------------------------------------
# Factory
# ----------------------------------------------------------------------
#

def build_node(

    node_id: str,

    node_type: str,

    label: str,

    *,
    workspace_id: Optional[int] = None,

    entity_id: Optional[Any] = None,

    status: Optional[str] = None,

    trust_tier: Optional[str] = None,

    verification: Optional[str] = None,

    origin: Optional[str] = None,

    provider: Optional[str] = None,

    created_at: Optional[datetime] = None,

    metadata: Optional[Dict[str, Any]] = None,

) -> Dict[str, Any]:

    metadata = metadata or {}

    return {

        "id":
            node_id,

        "type":
            node_type,

        "label":
            label,

        "workspace_id":
            workspace_id,

        "entity_id":
            entity_id,

        "status":
            status,

        "trust_tier":
            trust_tier,

        "verification":
            verification,

        "origin":
            origin,

        "provider":
            provider,

        "created_at":
            created_at.isoformat()
            if isinstance(created_at, datetime)
            else created_at,

        "color":
            NODE_COLORS.get(
                node_type,
                "#64748B",
            ),

        "icon":
            NODE_ICONS.get(
                node_type,
                "circle",
            ),

        "metadata":
            metadata,
    }


#
# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------
#

def validate_node(
    node: Dict[str, Any],
) -> None:

    required = [

        "id",

        "type",

        "label",

        "metadata",
    ]

    for field in required:

        if field not in node:

            raise ValueError(
                f"Missing node field: {field}"
            )


#
# ----------------------------------------------------------------------
# Convenience Builders
# ----------------------------------------------------------------------
#

def build_claim_node(**kwargs):
    return build_node(
        node_type=NODE_CLAIM,
        **kwargs,
    )


def build_trade_node(**kwargs):
    return build_node(
        node_type=NODE_TRADE,
        **kwargs,
    )


def build_import_batch_node(**kwargs):
    return build_node(
        node_type=NODE_IMPORT_BATCH,
        **kwargs,
    )


def build_broker_connection_node(**kwargs):
    return build_node(
        node_type=NODE_BROKER_CONNECTION,
        **kwargs,
    )


def build_broker_account_node(**kwargs):
    return build_node(
        node_type=NODE_BROKER_ACCOUNT,
        **kwargs,
    )


def build_snapshot_node(**kwargs):
    return build_node(
        node_type=NODE_ACCOUNT_SNAPSHOT,
        **kwargs,
    )


def build_audit_node(**kwargs):
    return build_node(
        node_type=NODE_AUDIT_EVENT,
        **kwargs,
    )


def build_integrity_alert_node(**kwargs):
    return build_node(
        node_type=NODE_INTEGRITY_ALERT,
        **kwargs,
    )


def build_integrity_scan_node(**kwargs):
    return build_node(
        node_type=NODE_INTEGRITY_SCAN,
        **kwargs,
    )


def build_risk_node(**kwargs):
    return build_node(
        node_type=NODE_RISK,
        **kwargs,
    )


def build_workspace_node(**kwargs):
    return build_node(
        node_type=NODE_WORKSPACE,
        **kwargs,
    )