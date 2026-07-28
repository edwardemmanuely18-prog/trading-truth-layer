from __future__ import annotations

from dataclasses import dataclass

from typing import Optional, Tuple

from app.services.authorization.registry.capability_catalog import *


# ============================================================
# Canonical Page Definition
# ============================================================


from typing import Optional

from app.services.authorization.registry.capability_catalog import *


@dataclass(frozen=True)
class PageDefinition:

    #
    # Canonical identifier
    #
    page: str

    title: str

    #
    # Frontend
    #
    urls: Tuple[str, ...]

    #
    # Backend
    #
    api_prefixes: Tuple[str, ...]

    #
    # Backward compatibility
    #
    allowed_roles: Tuple[str, ...]

    #
    # IAM
    #
    required_capabilities: Tuple[str, ...] = ()

    #
    # Commercial
    #
    required_feature: Optional[str] = None


# ============================================================
# Workspace Pages
# ============================================================


PAGE_REGISTRY = {

    # --------------------------------------------------------
    # Dashboard
    # --------------------------------------------------------

    "dashboard": PageDefinition(

        page="dashboard",

        title="Dashboard",

        urls=(

            "/workspace/{workspace_id}/dashboard",

        ),

        api_prefixes=(

            "/dashboard",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",
            "member",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    # --------------------------------------------------------
    # Evidence Intake
    # --------------------------------------------------------

    "broker_connections": PageDefinition(

        page="broker_connections",

        title="Broker Connections",

        urls=(

            "/workspace/{workspace_id}/broker-connections",

        ),

        api_prefixes=(

            "/broker-connections",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "import_center": PageDefinition(

        page="import_center",

        title="Import Center",

        urls=(

            "/workspace/{workspace_id}/import-center",
            "/workspace/{workspace_id}/import",

        ),

        api_prefixes=(

            "/imports",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "sync_jobs": PageDefinition(

        page="sync_jobs",

        title="Sync Jobs",

        urls=(

            "/workspace/{workspace_id}/sync-jobs",

        ),

        api_prefixes=(

            "/sync-jobs",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "adapter_registry": PageDefinition(

        page="adapter_registry",

        title="Adapter Registry",

        urls=(

            "/workspace/{workspace_id}/adapter-registry",

        ),

        api_prefixes=(

            "/adapter-registry",

        ),

        allowed_roles=(

            "owner",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    # --------------------------------------------------------
    # Evidence Registry
    # --------------------------------------------------------

    "ledger": PageDefinition(

        page="ledger",

        title="Trade Ledger",

        urls=(

            "/workspace/{workspace_id}/ledger",

        ),

        api_prefixes=(

            "/ledger",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "evidence_records": PageDefinition(

        page="evidence_records",

        title="Evidence Records",

        urls=(

            "/workspace/{workspace_id}/evidence-records",

        ),

        api_prefixes=(

            "/evidence-records",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "import_batches": PageDefinition(

        page="import_batches",

        title="Import Batches",

        urls=(

            "/workspace/{workspace_id}/import-batches",

        ),

        api_prefixes=(

            "/import-batches",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "audit_timeline": PageDefinition(

        page="audit_timeline",

        title="Audit Timeline",

        urls=(

            "/workspace/{workspace_id}/audit-timeline",

        ),

        api_prefixes=(

            "/audit",

        ),

        allowed_roles=(

            "owner",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "integrity_registry": PageDefinition(

        page="integrity_registry",

        title="Integrity Registry",

        urls=(

            "/workspace/{workspace_id}/integrity-registry",

        ),

        api_prefixes=(

            "/integrity",

        ),

        allowed_roles=(

            "owner",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    # --------------------------------------------------------
    # Claim Operations
    # --------------------------------------------------------

    "claims": PageDefinition(

        page="claims",

        title="Claims",

        urls=(

            "/workspace/{workspace_id}/claims",

        ),

        api_prefixes=(

            "/claims",

        ),

        allowed_roles=(

            "owner",
            "operator",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "claim_builder": PageDefinition(

        page="claim_builder",

        title="Claim Builder",

        urls=(

            "/schema",

        ),

        api_prefixes=(

            "/schema",

        ),

        allowed_roles=(

            "owner",
            "operator",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "claim_review": PageDefinition(

        page="claim_review",

        title="Evidence Review",

        urls=(

            "/workspace/{workspace_id}/evidence",

        ),

        api_prefixes=(

            "/evidence",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "schema_registry": PageDefinition(

        page="schema_registry",

        title="Schema Registry",

        urls=(

            "/workspace/{workspace_id}/schema",

        ),

        api_prefixes=(

            "/schema",

        ),

        allowed_roles=(

            "owner",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    "templates": PageDefinition(

        page="templates",

        title="Templates",

        urls=(

            "/workspace/{workspace_id}/claim-templates",

        ),

        api_prefixes=(

            "/claim-templates",

        ),

        allowed_roles=(

            "owner",

        ),

        required_capabilities=(

            MEMBER_READ,

        ),

        required_feature="workspace_members",

    ),

    # --------------------------------------------------------
    # Trust Intelligence
    # --------------------------------------------------------

    "trust_scores": PageDefinition(
        page="trust_scores",
        title="Trust Scores",
        urls=("/workspace/{workspace_id}/trust-scores",),
        api_prefixes=("/trust-scores",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "leaderboard": PageDefinition(
        page="leaderboard",
        title="Leaderboard",
        urls=("/workspace/{workspace_id}/leaderboard",),
        api_prefixes=("/leaderboard",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "verification_analytics": PageDefinition(
        page="verification_analytics",
        title="Verification Analytics",
        urls=("/workspace/{workspace_id}/verification-analytics",),
        api_prefixes=("/verification-analytics",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "integrity_analytics": PageDefinition(
        page="integrity_analytics",
        title="Integrity Analytics",
        urls=("/workspace/{workspace_id}/integrity-analytics",),
        api_prefixes=("/integrity-analytics",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "evidence_analytics": PageDefinition(
        page="evidence_analytics",
        title="Evidence Analytics",
        urls=("/workspace/{workspace_id}/evidence-analytics",),
        api_prefixes=("/evidence-analytics",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    # --------------------------------------------------------
    # Investigation Center
    # --------------------------------------------------------

    "investigation_overview": PageDefinition(

        page="investigation_overview",

        title="Investigation Overview",

        urls=(

            "/workspace/{workspace_id}/investigation-overview",

            "/workspace/{workspace_id}/investigations",

        ),

        api_prefixes=(

            "/investigation-overview",

            "/investigations",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "investigation_timeline": PageDefinition(

        page="investigation_timeline",

        title="Investigation Timeline",

        urls=(

            "/workspace/{workspace_id}/investigation-timeline",

        ),

        api_prefixes=(

            "/investigation-timeline",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "investigation_evidence": PageDefinition(

        page="investigation_evidence",

        title="Investigation Evidence",

        urls=(

            "/workspace/{workspace_id}/investigation-evidence",

        ),

        api_prefixes=(

            "/investigation-evidence",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "investigation_domains": PageDefinition(

        page="investigation_domains",

        title="Investigation Domains",

        urls=(

            "/workspace/{workspace_id}/investigation-domains",

        ),

        api_prefixes=(

            "/investigation-domains",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "investigation_findings": PageDefinition(

        page="investigation_findings",

        title="Investigation Findings",

        urls=(

            "/workspace/{workspace_id}/investigation-findings",

        ),

        api_prefixes=(

            "/investigation-findings",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "investigation_reports": PageDefinition(

        page="investigation_reports",

        title="Investigation Reports",

        urls=(

            "/workspace/{workspace_id}/investigation-reports",

        ),

        api_prefixes=(

            "/reports/workspace",

        ),

        allowed_roles=(

            "owner",
            "operator",
            "auditor",

        ),

        required_capabilities=(

            INVESTIGATION_READ,

        ),

        required_feature="investigations",

    ),

    "risk_analytics": PageDefinition(
        page="risk_analytics",
        title="Risk Analytics",
        urls=("/workspace/{workspace_id}/risk-analytics",),
        api_prefixes=("/risk-analytics",),
        allowed_roles=(
            "owner",
            "auditor",
        ),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "allocator_reports": PageDefinition(
        page="allocator_reports",
        title="Allocator Reports",
        urls=("/workspace/{workspace_id}/due-diligence",),
        api_prefixes=("/allocator",),
        allowed_roles=(
            "owner",
            "auditor",
        ),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "report_center": PageDefinition(
        page="report_center",
        title="Report Center",
        urls=("/workspace/{workspace_id}/report-center",),
        api_prefixes=("/report-center",),
        allowed_roles=(
            "owner",
            "auditor",
        ),  
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    # --------------------------------------------------------
    # Administration
    # --------------------------------------------------------

    "members": PageDefinition(
        page="members",
        title="Members",
        urls=("/workspace/{workspace_id}/members",),
        api_prefixes=("/members",),
        allowed_roles=(
            "owner",
            "auditor",
        ),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "roles": PageDefinition(
        page="roles",
        title="Roles",
        urls=("/workspace/{workspace_id}/roles",),
        api_prefixes=("/roles",),
        allowed_roles=("owner",),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "billing": PageDefinition(
        page="billing",
        title="Billing",
        urls=("/workspace/{workspace_id}/billing",),
        api_prefixes=("/billing",),
        allowed_roles=("owner",),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "settings": PageDefinition(
        page="settings",
        title="Settings",
        urls=("/workspace/{workspace_id}/settings",),
        api_prefixes=("/settings",),
        allowed_roles=("owner",),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

    "audit_logs": PageDefinition(
        page="audit_logs",
        title="Audit Logs",
        urls=("/workspace/{workspace_id}/audit-logs",),
        api_prefixes=("/audit-logs",),
        allowed_roles=("owner", "auditor"),
        required_capabilities=(
            MEMBER_READ,
        ),
        required_feature="workspace_members",
    ),

}